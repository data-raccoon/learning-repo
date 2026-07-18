"""
Vector Earth — FastAPI application entry point.

Start the server:
    uvicorn backend.main:app --reload

API docs available at:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.geo import router as geo_router

app = FastAPI(
    title="Vector Earth API",
    description="Serves geospatial layers from the local SQLite + SpatiaLite database.",
    version="0.1.0",
)

# Allow all origins for local development so the browser frontend can call
# the API regardless of how index.html is served (file://, localhost:3000, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(geo_router)


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Vector Earth API is running. See /docs for available endpoints."}
