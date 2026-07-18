"""
Natural Earth ingestion script
-------------------------------
Downloads the 1:10m Admin-0 Countries shapefile from Natural Earth (no account
or token required), reprojects to WGS84, and loads the data into the local
SpatiaLite database at db/vector_earth.db.

Safe to re-run: the 'countries' table is dropped and recreated each time.

Usage:
    python ingest/load_natural_earth.py

SpatiaLite on Windows
---------------------
Set the environment variable SPATIALITE_LIBRARY_PATH to the full path of
mod_spatialite.dll, e.g.:
    set SPATIALITE_LIBRARY_PATH=C:\\OSGeo4W\\bin\\mod_spatialite.dll
If not set, the script tries "mod_spatialite" (relies on PATH / DLL search order).
"""

import os
import pathlib
import warnings
import zipfile

import geopandas as gpd
import requests
from sqlalchemy import create_engine, event, text

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "db" / "vector_earth.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Natural Earth source
# ---------------------------------------------------------------------------
NE_URL = (
    "https://naturalearth.s3.amazonaws.com"
    "/10m_cultural/ne_10m_admin_0_countries.zip"
)
ZIP_PATH = DATA_DIR / "ne_10m_admin_0_countries.zip"
SHP_NAME = "ne_10m_admin_0_countries.shp"

# Columns to retain (beyond geometry); lowercase after normalisation
KEEP_COLS = ["name", "continent", "iso_a3", "pop_est", "gdp_md"]


# ---------------------------------------------------------------------------
# Step 1 — Download (skip if already present)
# ---------------------------------------------------------------------------
def download_shapefile() -> None:
    if ZIP_PATH.exists():
        print(f"[ingest] Zip already present at {ZIP_PATH}, skipping download.")
        return
    print(f"[ingest] Downloading Natural Earth 1:10m countries …\n  {NE_URL}")
    response = requests.get(NE_URL, timeout=60)
    response.raise_for_status()
    ZIP_PATH.write_bytes(response.content)
    print(f"[ingest] Saved {len(response.content) / 1024:.0f} KB → {ZIP_PATH}")


# ---------------------------------------------------------------------------
# Step 2 — Read shapefile into GeoDataFrame
# ---------------------------------------------------------------------------
def read_geodataframe() -> gpd.GeoDataFrame:
    print("[ingest] Extracting and reading shapefile …")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(DATA_DIR)

    gdf = gpd.read_file(DATA_DIR / SHP_NAME)

    # Normalise column names to lowercase
    gdf.columns = [c.lower() for c in gdf.columns]

    # Keep only the columns we care about (ignore missing ones gracefully)
    cols = [c for c in KEEP_COLS if c in gdf.columns] + ["geometry"]
    gdf = gdf[cols]

    # Ensure WGS84
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        print("[ingest] Reprojecting to WGS84 (EPSG:4326) …")
        gdf = gdf.to_crs(epsg=4326)

    print(f"[ingest] {len(gdf)} features, columns: {list(gdf.columns)}")
    return gdf


# ---------------------------------------------------------------------------
# Step 3 — Write to SpatiaLite
# ---------------------------------------------------------------------------
def _get_spatialite_lib() -> str:
    """Return the SpatiaLite library path, honoring SPATIALITE_LIBRARY_PATH."""
    lib = os.environ.get("SPATIALITE_LIBRARY_PATH", "mod_spatialite")
    # On Windows, ensure the DLL's own directory is in the process DLL search
    # path so its dependencies (GEOS, PROJ, etc.) are found at load time.
    lib_path = pathlib.Path(lib)
    if lib_path.is_absolute() and lib_path.parent.exists():
        os.add_dll_directory(str(lib_path.parent))
    return lib


def write_to_spatialite(gdf: gpd.GeoDataFrame) -> None:
    lib = _get_spatialite_lib()
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # Load the SpatiaLite extension on every new connection
    @event.listens_for(engine, "connect")
    def load_spatialite(dbapi_conn, _):
        dbapi_conn.enable_load_extension(True)
        try:
            dbapi_conn.load_extension(lib)
        except Exception as exc:
            raise RuntimeError(
                f"Could not load SpatiaLite extension from '{lib}'.\n"
                "On Windows, set SPATIALITE_LIBRARY_PATH to the full path of\n"
                "mod_spatialite.dll, e.g.:\n"
                "  set SPATIALITE_LIBRARY_PATH=C:\\OSGeo4W\\bin\\mod_spatialite.dll\n"
                "Ensure all dependency DLLs (GEOS, PROJ, etc.) are in the same\n"
                "directory or on PATH. See README.md for details."
            ) from exc

    print(f"[ingest] Writing 'countries' table to {DB_PATH} …")

    # Encode geometry as WKB hex for SQLite storage (SpatiaLite reads WKB).
    # to_postgis generates PostgreSQL-specific DDL and won't work with SQLite,
    # so we serialise geometry manually and write via plain pandas to_sql.
    df = gdf.copy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        df["geometry"] = gdf.geometry.apply(lambda geom: geom.wkb_hex if geom else None)

    with engine.begin() as conn:
        # Drop and recreate for idempotency
        conn.execute(text("DROP TABLE IF EXISTS countries"))
        df.to_sql(
            name="countries",
            con=conn,
            if_exists="replace",
            index=True,
            index_label="id",
        )
        _write_metadata(conn)

    # Verify
    with engine.connect() as conn:
        row_count = conn.execute(text("SELECT COUNT(*) FROM countries")).scalar()
        sample = conn.execute(text("SELECT name FROM countries LIMIT 1")).scalar()

    print(f"[ingest] Done. {row_count} rows written. Sample name: '{sample}'")


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

# Descriptions for the layer_metadata table.
# Each entry: (table_name, column_name_or_None, description)
# A row with column_name IS NULL describes the table itself.
_METADATA = [
    ("countries", None,         "One row per country/territory. Source: Natural Earth 1:10m Admin-0 (public domain). Geometry is WKB hex, EPSG:4326."),
    ("countries", "id",         "Auto-assigned integer primary key."),
    ("countries", "name",       "Country or territory name (English)."),
    ("countries", "continent",  "Continent name as assigned by Natural Earth (e.g. 'Europe', 'Asia', 'Africa')."),
    ("countries", "iso_a3",     "ISO 3166-1 alpha-3 country code. May be '-99' for disputed or unrecognised territories."),
    ("countries", "pop_est",    "Estimated population (Natural Earth attribute, approximate)."),
    ("countries", "gdp_md",     "Estimated GDP in millions of USD (Natural Earth attribute, approximate)."),
    ("countries", "geometry",   "Country polygon or multipolygon encoded as WKB hex string, coordinate reference system EPSG:4326 (WGS84)."),
]


def _write_metadata(conn) -> None:
    """Create (or replace) the layer_metadata table and populate it."""
    conn.execute(text("DROP TABLE IF EXISTS layer_metadata"))
    conn.execute(text("""
        CREATE TABLE layer_metadata (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name  TEXT    NOT NULL,
            column_name TEXT,
            description TEXT    NOT NULL
        )
    """))
    conn.execute(
        text("INSERT INTO layer_metadata (table_name, column_name, description) VALUES (:t, :c, :d)"),
        [{"t": t, "c": c, "d": d} for t, c, d in _METADATA],
    )
    print(f"[ingest] Metadata written ({len(_METADATA)} rows in layer_metadata).")


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
def cleanup_intermediate_files() -> None:
    """Remove downloaded zip and extracted shapefile components from data/."""
    removed = []
    for path in DATA_DIR.iterdir():
        if path.name != ".gitkeep":
            path.unlink()
            removed.append(path.name)
    if removed:
        print(f"[ingest] Removed: {', '.join(removed)}")
    else:
        print("[ingest] Nothing to clean up.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Natural Earth ingestion script.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove intermediate files from data/ (zip + extracted shapefile components).",
    )
    args = parser.parse_args()

    if args.clean:
        cleanup_intermediate_files()
    else:
        download_shapefile()
        gdf = read_geodataframe()
        write_to_spatialite(gdf)
