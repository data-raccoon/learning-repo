"""
Geo router — serves GeoJSON layers from the SQLite database.

Endpoints
---------
GET /layers
    Returns a list of available layer names, discovered dynamically from
    layer_metadata (one entry per table where column_name IS NULL).

GET /layers/{layer_name}
    Returns a GeoJSON FeatureCollection for the requested layer.
    Currently supported: 'countries'.
    Returns 404 for unknown layer names.
"""

from fastapi import APIRouter, HTTPException
from shapely import wkb
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry import mapping
from shapely.validation import make_valid

from backend.database import Country, LayerMetadata, get_session

# Simplification tolerance in degrees (~1 km at equator).
# Removes near-duplicate vertices that cause Cesium's tessellator to overflow.
_SIMPLIFY_TOLERANCE = 0.01
_MAX_SIMPLIFY_TOLERANCE = 0.2
_MAX_COORDINATES = 6000
_COUNTRY_COLOR_COUNT = 8
_NEARBY_COUNTRY_DISTANCE_DEGREES = 2.0

router = APIRouter(prefix="/layers", tags=["layers"])

# Map layer name → ORM model. Add entries here when new layers are ingested.
_LAYER_MODELS = {
    "countries": Country,
}


def _polygonal_only(geom):
    """Return only polygonal components from possibly mixed geometry output."""
    if geom.is_empty:
        return None
    if isinstance(geom, (Polygon, MultiPolygon)):
        return geom

    geoms = getattr(geom, "geoms", None)
    if not geoms:
        return None

    polygons = []
    for part in geoms:
        if isinstance(part, Polygon):
            polygons.append(part)
        elif isinstance(part, MultiPolygon):
            polygons.extend(list(part.geoms))

    if not polygons:
        return None
    if len(polygons) == 1:
        return polygons[0]
    return MultiPolygon(polygons)


def _largest_polygon(geom):
    """Return the largest polygon component from a polygonal geometry."""
    geom = _polygonal_only(geom)
    if geom is None or geom.is_empty:
        return None
    if isinstance(geom, Polygon):
        return geom
    polygons = list(geom.geoms)
    if not polygons:
        return None
    return max(polygons, key=lambda poly: poly.area)


def _focus_point(geom) -> tuple[float, float] | None:
    """Return a stable point on land for camera focus."""
    polygon = _largest_polygon(geom)
    if polygon is None or polygon.is_empty:
        return None
    point = polygon.representative_point()
    return (point.x, point.y)


def _coordinate_count(geom) -> int:
    """Count vertices across polygon exteriors and holes."""
    if geom.is_empty:
        return 0

    polygons = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    total = 0
    for poly in polygons:
        total += len(poly.exterior.coords)
        total += sum(len(ring.coords) for ring in poly.interiors)
    return total


def _simplify_for_cesium(geom):
    """Progressively simplify geometry until it is lightweight enough for Cesium."""
    geom = _polygonal_only(geom)
    if geom is None or geom.is_empty:
        return None

    tolerance = _SIMPLIFY_TOLERANCE
    simplified = geom.simplify(tolerance, preserve_topology=True)
    simplified = _polygonal_only(simplified)

    while (
        simplified is not None
        and not simplified.is_empty
        and _coordinate_count(simplified) > _MAX_COORDINATES
        and tolerance < _MAX_SIMPLIFY_TOLERANCE
    ):
        tolerance = min(tolerance * 2, _MAX_SIMPLIFY_TOLERANCE)
        simplified = geom.simplify(tolerance, preserve_topology=True)
        simplified = _polygonal_only(simplified)

    return simplified


def _bounds_intersect(bounds_a, bounds_b) -> bool:
    """Cheap bounding-box overlap test before more expensive geometry work."""
    min_ax, min_ay, max_ax, max_ay = bounds_a
    min_bx, min_by, max_bx, max_by = bounds_b
    return (
        min_ax <= max_bx
        and max_ax >= min_bx
        and min_ay <= max_by
        and max_ay >= min_by
    )


def _bounds_intersect_with_margin(bounds_a, bounds_b, margin: float) -> bool:
    """Bounding-box overlap test that allows a configurable padding margin."""
    min_ax, min_ay, max_ax, max_ay = bounds_a
    min_bx, min_by, max_bx, max_by = bounds_b
    return (
        (min_ax - margin) <= max_bx
        and (max_ax + margin) >= min_bx
        and (min_ay - margin) <= max_by
        and (max_ay + margin) >= min_by
    )


def _share_border(geom_a, geom_b) -> bool:
    """Return True when two polygonal geometries share any boundary points."""
    if geom_a is None or geom_b is None:
        return False
    if geom_a.is_empty or geom_b.is_empty:
        return False
    if not _bounds_intersect(geom_a.bounds, geom_b.bounds):
        return False
    if geom_a.disjoint(geom_b):
        return False
    return not geom_a.boundary.intersection(geom_b.boundary).is_empty


def _are_visually_close(geom_a, geom_b) -> bool:
    """Return True when countries are close enough that matching colors look confusing."""
    if geom_a is None or geom_b is None:
        return False
    if geom_a.is_empty or geom_b.is_empty:
        return False
    if not _bounds_intersect_with_margin(
        geom_a.bounds,
        geom_b.bounds,
        _NEARBY_COUNTRY_DISTANCE_DEGREES,
    ):
        return False
    return geom_a.distance(geom_b) <= _NEARBY_COUNTRY_DISTANCE_DEGREES


def _countries_conflict(geom_a, geom_b) -> bool:
    """Return True when countries should avoid sharing the same map color."""
    return _share_border(geom_a, geom_b) or _are_visually_close(geom_a, geom_b)


def _assign_country_color_groups(items: list[dict]) -> None:
    """Greedy graph coloring so neighboring or near-neighbor countries differ."""
    adjacency: list[set[int]] = [set() for _ in items]

    for i, item in enumerate(items):
        geom_i = item["adjacency_geom"]
        for j in range(i + 1, len(items)):
            geom_j = items[j]["adjacency_geom"]
            if _countries_conflict(geom_i, geom_j):
                adjacency[i].add(j)
                adjacency[j].add(i)

    order = sorted(range(len(items)), key=lambda idx: len(adjacency[idx]), reverse=True)

    for idx in order:
        used_colors = {
            items[neighbor]["properties"].get("color_group")
            for neighbor in adjacency[idx]
            if items[neighbor]["properties"].get("color_group") is not None
        }

        color_group = 0
        while color_group in used_colors:
            color_group += 1

        items[idx]["properties"]["color_group"] = color_group % _COUNTRY_COLOR_COUNT


# ---------------------------------------------------------------------------
# GET /layers
# ---------------------------------------------------------------------------
@router.get("", summary="List available layers")
def list_layers() -> list[dict]:
    """
    Returns all layer names registered in layer_metadata, with their
    table-level description.
    """
    with get_session() as session:
        rows = (
            session.query(LayerMetadata)
            .filter(LayerMetadata.column_name == None)  # noqa: E711
            .order_by(LayerMetadata.table_name)
            .all()
        )
    return [{"name": r.table_name, "description": r.description} for r in rows]


# ---------------------------------------------------------------------------
# GET /layers/{layer_name}
# ---------------------------------------------------------------------------
@router.get("/{layer_name}", summary="Get a layer as GeoJSON")
def get_layer(layer_name: str) -> dict:
    """
    Returns a GeoJSON FeatureCollection for the given layer name.
    Geometry is decoded from WKB hex and serialised to GeoJSON coordinates.
    Properties include all non-geometry columns.
    """
    model = _LAYER_MODELS.get(layer_name)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Layer '{layer_name}' not found.")

    with get_session() as session:
        rows = session.query(model).all()

    render_items = []
    for row in rows:
        if not row.geometry:
            continue
        raw_geom = wkb.loads(bytes.fromhex(row.geometry))
        adjacency_geom = _polygonal_only(make_valid(raw_geom))
        if adjacency_geom is None or adjacency_geom.is_empty:
            continue
        # Fix invalid rings, keep only polygonal output, and simplify until the
        # geometry is small enough for Cesium's worker pipeline to handle.
        render_geom = _simplify_for_cesium(adjacency_geom)
        if render_geom is None or render_geom.is_empty:
            continue
        # Collect all non-geometry columns as feature properties
        props = {
            col: getattr(row, col)
            for col in model.__table__.columns.keys()
            if col != "geometry"
        }
        focus_point = _focus_point(adjacency_geom)
        if focus_point is not None:
            props["focus_lon"] = focus_point[0]
            props["focus_lat"] = focus_point[1]
        render_items.append({
            "geometry": mapping(render_geom),
            "properties": props,
            "adjacency_geom": adjacency_geom,
        })

    if layer_name == "countries":
        _assign_country_color_groups(render_items)

    features = []
    for item in render_items:
        features.append({
            "type": "Feature",
            "geometry": item["geometry"],
            "properties": item["properties"],
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }
