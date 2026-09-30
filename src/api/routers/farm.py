"""Farmer profile, farm context and dashboard stats."""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api import repository
from src.api.security import current_farm_id
from src.zone1_edge.context.farm_context import INDIAN_REGIONS
from src.zone3_memory.db import farm_memory

router = APIRouter(tags=["farm"])


class ProfileUpdate(BaseModel):
    region: str | None = None


@router.get("/me")
def me(farm_id: str = Depends(current_farm_id)) -> dict:
    profile = repository.get_profile(farm_id)
    if not profile:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account not found.")
    return profile


@router.patch("/me")
def update_me(body: ProfileUpdate, farm_id: str = Depends(current_farm_id)) -> dict:
    if body.region is not None:
        if body.region not in INDIAN_REGIONS:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown region.")
        farm_memory.update_farm_location(farm_id, body.region)
    return me(farm_id)


@router.get("/stats")
def stats(farm_id: str = Depends(current_farm_id)) -> dict:
    rows = repository.list_history(farm_id)
    healthy = sum(1 for r in rows if "healthy" in (r["condition"] or "").lower())
    routes = Counter(r["route"] for r in rows)
    return {
        "total": len(rows),
        "crop": sum(1 for r in rows if r["domain"] == "crop"),
        "livestock": sum(1 for r in rows if r["domain"] == "livestock"),
        "healthy": healthy,
        "needs_attention": len(rows) - healthy,
        "offline": routes.get("local", 0),
        "cloud": routes.get("cloud", 0),
        "last_check_at": rows[0]["created_at"] if rows else None,
    }
