# Vector Earth — Implementation Plan

## Overview

Build a minimal, local 3D geo-visualization tool that displays continent/country shapes on an interactive WebGL globe. Geospatial data is stored in a standards-compliant SQL database (SQLite + SpatiaLite), which is the **single source of truth** — the API reads exclusively from it and never proxies external services. Data is populated once via an ingestion script that downloads freely available Natural Earth shapefiles (no account or token required). The architecture is designed so that additional datasets and layers can be added later with no structural changes.

**Scope:** Data ingestion → API → Browser frontend
**Out of scope (for now):** Jupyter notebook, user authentication, deployment, satellite imagery (hook is prepared)

---

## Sub-Task 1 — Project Scaffolding

**Status:** `[x] done`

**Intent**  
Set up the project directory structure, virtual environment, and dependency list so every subsequent sub-task has a clean, reproducible foundation to build on.

**Expected Outcomes**
- Project folders exist as specified below
- `requirements.txt` lists all needed packages
- A `README.md` describes how to install dependencies and run the project

**Todo List**
1. Create the directory tree: `data/`, `db/`, `ingest/`, `backend/routers/`, `frontend/`
2. Create `requirements.txt` with: `fastapi`, `uvicorn`, `sqlalchemy`, `geoalchemy2`, `geopandas`, `fiona`, `shapely`, `requests`
3. Create a minimal `README.md` with:
   - Generic install instructions for SpatiaLite (note that the package name varies by OS — e.g. `libsqlite3-mod-spatialite` on Debian/Ubuntu, `spatialite-tools` via Homebrew on macOS, pre-built DLL on Windows — and link to the official SpatiaLite site)
   - Steps: install Python deps → run ingest → run server → open browser

**Relevant Context**
- No existing files in workspace — clean slate
- SpatiaLite is a C extension to SQLite; it must be loaded at runtime via `load_extension`. Note this in the README.
- Keep README instructions generic (no OS-specific commands); point users to official docs for platform-specific steps

---

## Sub-Task 2 — Data Ingestion Pipeline

**Status:** `[x] done`

**Intent**
Download Natural Earth continent/country polygon data (no token or account required) and load it into the SpatiaLite database, which becomes the single source of truth for all subsequent API queries.

**Expected Outcomes**
- `db/vector_earth.db` exists and contains a `countries` table with geometry (WGS84) and attribute columns (name, continent, iso_a3, pop_est, etc.)
- Running `python ingest/load_natural_earth.py` is idempotent (safe to re-run, drops and recreates the table)
- Geometries are stored as WKB in a proper spatial column registered with SpatiaLite metadata

**Todo List**
1. In `ingest/load_natural_earth.py`, download the Natural Earth **1:10m Admin-0 Countries** shapefile directly from the Natural Earth GitHub mirror (`https://github.com/nvkelso/natural-earth-vector`) or the canonical URL (`https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip`) using `requests` — no account or token needed
2. Unzip into `data/` and read the `.shp` file into a GeoDataFrame using GeoPandas
3. Reproject to WGS84 (EPSG:4326) if not already
4. Create the SQLite DB at `db/vector_earth.db`, load the SpatiaLite extension
5. Write the GeoDataFrame to the DB as the `countries` table using GeoPandas + SQLAlchemy engine (drop table first if it exists to stay idempotent)
6. Verify by querying the row count and printing a sample feature name

**Relevant Context**
- The DB is the **only** data source the API will ever query — all future datasets must be ingested here first
- Use 1:10m resolution for reasonably detailed continent shapes; 1:110m is too coarse
- SpatiaLite extension loading: `connection.enable_load_extension(True)` then `connection.load_extension("mod_spatialite")`
- The `countries` table should have at minimum: `id`, `name`, `continent`, `iso_a3`, `geometry` (MultiPolygon, EPSG:4326)
- Store additional Natural Earth attributes (pop_est, etc.) as plain columns for future use

---

## Sub-Task 3 — FastAPI Backend

**Status:** `[x] done`

**Intent**  
Expose the database contents as a GeoJSON REST API so the frontend (and future clients) can fetch layers by name without knowing anything about the database internals.

**Expected Outcomes**
- `GET /layers/countries` returns a valid GeoJSON FeatureCollection of all country polygons
- `GET /layers` returns a list of available layer names (extensible for future datasets)
- CORS is enabled so the browser frontend (served from a different port or file) can call the API
- Server starts with `uvicorn backend.main:app --reload`

**Todo List**
1. Create `backend/database.py`: SQLAlchemy engine pointing to `db/vector_earth.db` (the DB is the sole data source), session factory, and a `Country` ORM model with a GeoAlchemy2 geometry column matching the ingested schema
2. Create `backend/routers/geo.py`: router with `GET /layers` (returns a list of available layer names derived from the DB, not hardcoded) and `GET /layers/{layer_name}` which queries the DB and serializes rows to a GeoJSON FeatureCollection using `geoalchemy2.shape.to_shape()` + `shapely.geometry.mapping()`
3. Create `backend/main.py`: FastAPI app, include the geo router, add CORSMiddleware (allow all origins for local dev)
4. Test manually: start the server, open `http://localhost:8000/layers/countries` in a browser and confirm valid GeoJSON

**Relevant Context**
- `geoalchemy2.shape.to_shape(geom)` converts a WKB column to a Shapely geometry
- Shapely geometry has a `.geojson` property for serialization (or use `shapely.geometry.mapping()`)
- The router pattern (`routers/geo.py`) makes it trivial to add `/layers/cities`, `/layers/rivers` etc. later

---

## Sub-Task 4 — CesiumJS Browser Frontend

**Status:** `[x] done`

**Intent**  
Build a single HTML page that renders a 3D interactive globe using CesiumJS and loads the country polygons from the FastAPI backend as a vector layer.

**Expected Outcomes**
- Opening `frontend/index.html` (via a simple file server or directly) shows a 3D globe with continent/country outlines rendered on the surface
- The globe is navigable (rotate, zoom, pan) with mouse/touch
- Country polygons are visually distinct from the background (filled or outlined)
- No build toolchain required — plain HTML + CDN-loaded CesiumJS

**Todo List**
1. In `frontend/index.html`, load CesiumJS from the official CDN (JS + CSS)
2. Initialize a `Viewer` with **no imagery** for now: use `baseLayer: false` (or `imageryProvider: false`) and set `Cesium.Ion.defaultAccessToken = ''` — no Cesium Ion account needed
3. Add a clearly marked `// IMAGERY HOOK` comment with a stubbed function `setImageryProvider(provider)` that, when called, swaps in a tile provider on the viewer — this is the single change needed to enable satellite imagery later
4. Fetch `http://localhost:8000/layers/countries` and load the GeoJSON into the viewer using `Cesium.GeoJsonDataSource.load()`
5. Style the polygons: semi-transparent fill, visible outline on a dark/neutral background
6. Fly the camera to a default overview position (e.g. slightly above the equator)
7. Add a comment block at the top of the HTML explaining how to add a new layer (fetch + `GeoJsonDataSource.load`) for future extensibility

**Relevant Context**
- CesiumJS CDN: `https://cesium.com/downloads/cesiumjs/releases/latest/Build/Cesium/`
- `GeoJsonDataSource.load()` accepts a URL or a GeoJSON object directly
- Imagery swap later: replace the `setImageryProvider` stub body with e.g. `new Cesium.OpenStreetMapImageryProvider(...)` or a token-based provider — no other code changes needed
- The `CORS` config from Sub-Task 3 must be in place before this works

---

## Notes for Future Sub-Tasks (not yet planned)

- **Additional layers:** Ingest new data into the DB → the `GET /layers` endpoint auto-discovers it → add a `GeoJsonDataSource` call in the frontend. No structural changes needed.
- **Satellite imagery:** Call the `setImageryProvider()` stub in `index.html` with any Cesium-compatible provider (OSM, Bing, custom WMS). The DB and API are unaffected.
- **Notebook:** A `notebooks/explore.ipynb` using `pydeck` can reuse the same `GET /layers/{name}` endpoint directly.
- **Attribute popups:** CesiumJS `ScreenSpaceEventHandler` can listen for clicks and display entity properties sourced from the GeoJSON `properties` object (already stored in the DB).
