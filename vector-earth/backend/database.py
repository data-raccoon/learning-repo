"""
Database engine, session factory, and ORM models.

The SQLite + SpatiaLite database at db/vector_earth.db is the sole data
source. Geometry is stored as WKB hex strings (plain TEXT column) and
decoded to Shapely geometries in the router layer.
"""

import os
import pathlib

from sqlalchemy import Column, Float, Integer, Text, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "vector_earth.db"

# ---------------------------------------------------------------------------
# SpatiaLite loader
# ---------------------------------------------------------------------------

def _load_spatialite(dbapi_conn, _):
    """Load the SpatiaLite extension on every new SQLite connection."""
    lib = os.environ.get("SPATIALITE_LIBRARY_PATH", "mod_spatialite")
    lib_path = pathlib.Path(lib)
    if lib_path.is_absolute() and lib_path.parent.exists():
        os.add_dll_directory(str(lib_path.parent))
    dbapi_conn.enable_load_extension(True)
    try:
        dbapi_conn.load_extension(lib)
    except Exception as exc:
        raise RuntimeError(
            f"Could not load SpatiaLite extension from '{lib}'.\n"
            "Set SPATIALITE_LIBRARY_PATH to the full path of mod_spatialite.dll.\n"
            "See README.md for details."
        ) from exc


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
engine = create_engine(f"sqlite:///{DB_PATH}")
event.listen(engine, "connect", _load_spatialite)


def get_session() -> Session:
    """Return a new SQLAlchemy session (caller is responsible for closing)."""
    return Session(engine)


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class Country(Base):
    """Maps to the 'countries' table created by the ingestion script."""
    __tablename__ = "countries"

    id        = Column(Integer, primary_key=True)
    name      = Column(Text)
    continent = Column(Text)
    iso_a3    = Column(Text)
    pop_est   = Column(Float)
    gdp_md    = Column(Integer)
    geometry  = Column(Text)   # WKB hex string, EPSG:4326


class LayerMetadata(Base):
    """Maps to the 'layer_metadata' table created by the ingestion script."""
    __tablename__ = "layer_metadata"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    table_name  = Column(Text, nullable=False)
    column_name = Column(Text)
    description = Column(Text, nullable=False)
