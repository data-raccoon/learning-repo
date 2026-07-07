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

    features = []
    for row in rows:
        if not row.geometry:
            continue
        geom = wkb.loads(bytes.fromhex(row.geometry))
        # Fix invalid rings, keep only polygonal output, and simplify until the
        # geometry is small enough for Cesium's worker pipeline to handle.
        geom = make_valid(geom)
        geom = _simplify_for_cesium(geom)
        if geom is None or geom.is_empty:
            continue
        # Collect all non-geometry columns as feature properties
        props = {
            col: getattr(row, col)
            for col in model.__table__.columns.keys()
            if col != "geometry"
        }
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": props,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }
