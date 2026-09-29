"""
weather_client.py — Zone 2 (cloud-only) weather context.

Provider: Open-Meteo forecast API (https://open-meteo.com) — free for
non-commercial use, NO API key, global coverage incl. all Indian states,
returns current temperature/humidity plus past-days precipitation in one call.
Zone 1 never imports this module (offline-first guarantee).

Disabled by default: set WEATHER_ENABLED=true to allow network calls.
Every failure (disabled, unknown region, timeout, bad JSON) returns None, and
the advisory is generated without weather context (graceful degradation).
Stdlib-only (urllib) to keep serverless bundles small.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT_S = float(os.environ.get("WEATHER_TIMEOUT_S", "4"))
_CACHE_TTL_S = 1800
_cache: dict[str, tuple[float, dict]] = {}

# Approximate state/UT centroids (lat, lon). Coarse by design: disease-risk
# weather context, not field-level forecasting. No geocoding API needed.
REGION_COORDS = {
    "andhra pradesh": (15.9, 79.7), "arunachal pradesh": (28.2, 94.7), "assam": (26.2, 92.9),
    "bihar": (25.1, 85.3), "chhattisgarh": (21.3, 81.9), "goa": (15.3, 74.1),
    "gujarat": (22.3, 71.2), "haryana": (29.1, 76.1), "himachal pradesh": (31.1, 77.2),
    "jharkhand": (23.6, 85.3), "karnataka": (15.3, 75.7), "kerala": (10.9, 76.3),
    "madhya pradesh": (22.97, 78.66), "maharashtra": (19.75, 75.71), "manipur": (24.7, 93.9),
    "meghalaya": (25.5, 91.4), "mizoram": (23.2, 92.9), "nagaland": (26.2, 94.6),
    "odisha": (20.95, 85.1), "punjab": (31.1, 75.3), "rajasthan": (27.0, 74.2),
    "sikkim": (27.5, 88.5), "tamil nadu": (11.1, 78.7), "telangana": (18.1, 79.0),
    "tripura": (23.9, 91.99), "uttar pradesh": (26.8, 80.9), "uttarakhand": (30.1, 79.0),
    "west bengal": (22.99, 87.9), "delhi": (28.7, 77.1), "jammu and kashmir": (33.8, 76.6),
    "ladakh": (34.2, 77.6), "puducherry": (11.9, 79.8),
}


def weather_enabled() -> bool:
    return os.environ.get("WEATHER_ENABLED", "false").lower() == "true"


def _http_get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=_TIMEOUT_S) as resp:  # noqa: S310 - fixed https host
        return json.loads(resp.read().decode("utf-8"))


def summarize(raw: dict) -> dict:
    """Reduce an Open-Meteo response to the disease-risk fields we forward."""
    cur = raw.get("current", {})
    rain = raw.get("daily", {}).get("precipitation_sum") or []
    rain_7d = round(sum(v for v in rain if v is not None), 1) if rain else None
    return {
        "temperature_c": cur.get("temperature_2m"),
        "relative_humidity_pct": cur.get("relative_humidity_2m"),
        "precipitation_last_7d_mm": rain_7d,
        "source": "open-meteo",
    }


def get_weather(region: str | None, fetch=_http_get_json) -> dict | None:
    """Return a small weather dict for `region`, or None (never raises)."""
    if not region or not weather_enabled():
        return None
    coords = REGION_COORDS.get(region.strip().lower())
    if not coords:
        return None
    key = region.strip().lower()
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < _CACHE_TTL_S:
        return hit[1]
    params = urllib.parse.urlencode({
        "latitude": coords[0], "longitude": coords[1],
        "current": "temperature_2m,relative_humidity_2m",
        "daily": "precipitation_sum", "past_days": 7, "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    })
    try:
        weather = summarize(fetch(f"{OPEN_METEO_URL}?{params}"))
    except Exception as e:  # noqa: BLE001 - degrade gracefully on any failure
        print(f"Weather unavailable ({type(e).__name__}); continuing without weather context.")
        return None
    _cache[key] = (time.time(), weather)
    return weather
