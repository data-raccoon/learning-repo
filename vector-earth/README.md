# Vector Earth

A minimal, local 3D geo-visualization tool. Country and continent shapes are stored in a local SQLite + SpatiaLite database and served via a FastAPI backend to a CesiumJS browser frontend.

---

## Prerequisites

### Python
Python 3.10 or newer is required.

### SpatiaLite
SpatiaLite is a geospatial extension to SQLite. It must be installed as a native shared library on your system before running the ingestion script.

| Platform | Typical method |
|----------|---------------|
| **Debian / Ubuntu** | `apt install libsqlite3-mod-spatialite` |
| **macOS** | `brew install spatialite-tools` |
| **Windows** | Download a pre-built `mod_spatialite.dll` (and its dependency DLLs) from the [SpatiaLite download page](https://www.gaia-gis.it/gaia-sins/). Then set the `SPATIALITE_LIBRARY_PATH` environment variable to the **full path** of `mod_spatialite.dll`, e.g. `C:\OSGeo4W\bin\mod_spatialite.dll`. Adding the directory to `PATH` alone is not always sufficient. |

For full platform-specific instructions, see the [official SpatiaLite site](https://www.gaia-gis.it/gaia-sins/).

> **Note:** SpatiaLite is loaded at runtime via SQLite's `load_extension` mechanism. Python's `sqlite3` module must be compiled with extension loading enabled (it is by default on most platforms; check with `sqlite3.sqlite_version`).

---

## Setup

### 1. Create and activate a virtual environment

This project uses a virtual environment at `%USERPROFILE%/vector-earth-venv` (Windows) / `$HOME/vector-earth-venv` (macOS/Linux).

Create it:
```
python -m venv %USERPROFILE%/vector-earth-venv
```

Activate it (platform-specific — use your shell's standard activation method, e.g. `Scripts\activate` on Windows or `bin/activate` on macOS/Linux).

### 2. Install Python dependencies

```
pip install -r requirements.txt
```

### 3. Run the data ingestion script

This downloads the Natural Earth Admin-0 Countries shapefile (1:10m resolution) and loads it into the local database at `db/vector_earth.db`. The script is safe to re-run.

```
python ingest/load_natural_earth.py
```

To remove the intermediate files from `data/` (zip archive and extracted shapefile components) after ingestion:

```
python ingest/load_natural_earth.py --clean
```

### 4. Start the API server

```
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

### 5. Open the frontend

Open `frontend/index.html` in your browser. It will connect to the local API and render the 3D globe.

> If your browser blocks requests from a `file://` URL, serve the frontend with any static file server, for example:
> ```
> python -m http.server 3000 --directory frontend
> ```
> Then open `http://localhost:3000`.

---

## Project Structure

```
vector-earth/
├── data/                        # Downloaded source shapefiles (auto-populated by ingest script)
├── db/                          # SQLite + SpatiaLite database (auto-created by ingest script)
│   └── vector_earth.db
├── ingest/
│   └── load_natural_earth.py    # Data ingestion: download → transform → load into DB
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # SQLAlchemy engine, session, and ORM models
│   └── routers/
│       └── geo.py               # /layers endpoints
├── frontend/
│   └── index.html               # CesiumJS 3D globe
└── requirements.txt
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/layers` | List all available layer names |
| `GET` | `/layers/{layer_name}` | Return a GeoJSON FeatureCollection for that layer |

---

## Adding a New Dataset (future)

1. Write an ingest script in `ingest/` that loads data into a new table in `db/vector_earth.db`
2. Add an ORM model for the new table in `backend/database.py`
3. The `GET /layers` endpoint will auto-discover it
4. In `frontend/index.html`, add a `Cesium.GeoJsonDataSource.load(...)` call for the new layer

---

## Enabling Satellite Imagery (future)

Look for the `// IMAGERY HOOK` comment in `frontend/index.html`. Replace the stub body with a Cesium-compatible imagery provider, for example:

```js
// OpenStreetMap (no token required)
setImageryProvider(new Cesium.OpenStreetMapImageryProvider({ url: 'https://tile.openstreetmap.org/' }));

// Or a token-based provider such as Bing or Cesium Ion World Imagery
```
