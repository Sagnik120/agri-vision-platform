"""Public, unauthenticated endpoints: health and static app metadata."""

from __future__ import annotations

import os

from fastapi import APIRouter

from src.api.config import settings
from src.zone1_edge.context.farm_context import INDIAN_REGIONS, SEASONS, infer_season

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict:
    gemini_ready = (
        os.environ.get("GEMINI_ENABLED", "false").lower() == "true"
        and bool(os.environ.get("GEMINI_API_KEY"))
        and os.environ.get("GEMINI_API_KEY") != "your_gemini_api_key_here"
    )
    return {
        "status": "ok",
        "expert_mode": settings.expert_mode,
        "advisory_backend": os.environ.get("ADVISORY_BACKEND", "gemini"),
        "cloud_ready": gemini_ready,  # never expose the key itself
    }


@router.get("/meta")
def meta() -> dict:
    return {
        "regions": INDIAN_REGIONS,
        "seasons": list(SEASONS),
        "current_season": infer_season(),
        "voice_enabled": settings.voice_enabled,
        "demo_otp": settings.demo_otp,
    }
