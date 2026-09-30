"""FastAPI application entry point. All routes are versioned under /api/v1."""

from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()  # before any zone module reads os.environ

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from src.api.config import settings  # noqa: E402
from src.api.routers import admin, auth, diagnoses, farm, meta  # noqa: E402
from src.zone3_memory.db import farm_memory  # noqa: E402


@asynccontextmanager
async def lifespan(_: FastAPI):
    farm_memory.init_db()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Agri-Vision API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (meta.router, auth.router, farm.router, diagnoses.router, admin.router):
    app.include_router(r, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "service": "Agri-Vision API",
        "website": "http://localhost:3000",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
