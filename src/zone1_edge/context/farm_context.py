"""
farm_context.py — Region / season context for Zone 1 (offline, no network).

Context NEVER changes the visual prediction or the moe_gate; it only adapts
advisory text (timing / preventive guidance) and is forwarded to Zone 2.
Weather is intentionally absent here: it is fetched cloud-side only (Zone 2).
"""

from __future__ import annotations

from datetime import date

from src.zone1_edge import config

INDIAN_REGIONS = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir", "Ladakh",
    "Puducherry",
]
SEASONS = ("kharif", "rabi", "zaid")


def infer_season(on: date | None = None) -> str:
    """Indian cropping season from month: kharif Jun-Oct, rabi Nov-Mar, zaid Apr-May."""
    m = (on or date.today()).month
    if 6 <= m <= 10:
        return "kharif"
    if m >= 11 or m <= 3:
        return "rabi"
    return "zaid"


def normalize_region(region: str | None) -> str | None:
    if not region:
        return None
    r = region.strip().lower()
    for name in INDIAN_REGIONS:
        if name.lower() == r:
            return name
    return region.strip()  # unknown regions are kept verbatim, never rejected


def build_context(region: str | None = None, season: str | None = None) -> dict:
    s = (season or "").strip().lower()
    season_source = "farmer" if s in SEASONS else "inferred_from_date"
    return {
        "region": normalize_region(region),
        "season": s if s in SEASONS else infer_season(),
        "season_source": season_source,
    }
