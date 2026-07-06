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
from shapely.geometry import mapping
from shapely.validation import make_valid

from backend.database import Country, LayerMetadata, get_session

# Simplification tolerance in degrees (~1 km at equator).
# Removes near-duplicate vertices that cause Cesium's tessellator to overflow.
_SIMPLIFY_TOLERANCE = 0.01

router = APIRouter(prefix="/layers", tags=["layers"])

# Map layer name → ORM model. Add entries here when new layers are ingested.
_LAYER_MODELS = {
    "countries": Country,
}


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
        # Fix invalid rings (self-intersections, etc.) then simplify to remove
        # the excessive vertex density that crashes Cesium's geometry pipeline.
        geom = make_valid(geom)
        geom = geom.simplify(_SIMPLIFY_TOLERANCE, preserve_topology=True)
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
