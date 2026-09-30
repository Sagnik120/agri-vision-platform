"""Admin portal: platform-wide analytics, farmer and diagnosis browsing, system health.

Read-only by design — the admin can inspect and export, never edit farm records.
Auth is a separate login (ADMIN_USERNAME / ADMIN_PASSWORD) issuing an "admin" token.
"""

from __future__ import annotations

import csv
import hmac
import io
import os
import platform
import sqlite3
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.api import diagnosis_service, translation
from src.api.config import PROJECT_ROOT, settings
from src.api.security import issue_token, read_token
from src.zone1_edge import config as zone1_config
from src.zone3_memory.db import farm_memory

router = APIRouter(prefix="/admin", tags=["admin"])
_bearer = HTTPBearer(auto_error=False)
_STARTED_AT = time.time()


def current_admin(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    claims = read_token(creds.credentials) if creds else None
    if not claims or claims.get("typ") != "admin":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Admin session expired. Please log in again.")
    return claims["sub"]


class AdminLogin(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: AdminLogin) -> dict:
    ok_user = hmac.compare_digest(body.username.strip(), settings.admin_username)
    ok_pass = hmac.compare_digest(body.password, settings.admin_password)
    if not (ok_user and ok_pass):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Username or password is incorrect.")
    token = issue_token({"typ": "admin", "sub": settings.admin_username}, ttl=settings.admin_token_ttl_seconds)
    return {"token": token, "username": settings.admin_username}


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(farm_memory.DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


_ALL_CHECKS_SQL = """
    SELECT o.observation_id, o.farm_id, o.created_at, o.domain, o.route, o.visual_confidence,
           o.image_prediction, o.farmer_text, o.sensor_json,
           d.condition, d.certainty, d.final_confidence,
           a.summary, a.source,
           f.farmer_name, f.phone, f.location
    FROM observations o
    JOIN diagnoses d ON o.observation_id = d.observation_id
    LEFT JOIN advisories a ON d.diagnosis_id = a.diagnosis_id
    LEFT JOIN farm f ON o.farm_id = f.farm_id
"""


def _all_checks() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(_ALL_CHECKS_SQL + " ORDER BY o.created_at DESC, o.observation_id DESC").fetchall()
    return [dict(r) for r in rows]


def _farmers() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT farm_id, phone, farmer_name, location, created_at FROM farm").fetchall()
    return [dict(r) for r in rows]


def _is_healthy(condition: str | None) -> bool:
    return "healthy" in (condition or "").lower()


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace(" ", "T")).replace(tzinfo=timezone.utc)


def _mask(phone: str | None) -> str:
    return f"{phone[:2]}••••••{phone[-2:]}" if phone and len(phone) >= 6 else (phone or "")


def _check_row(r: dict) -> dict:
    return {
        "id": r["observation_id"],
        "created_at": r["created_at"],
        "farm_id": r["farm_id"],
        "farmer_name": r["farmer_name"] or "—",
        "region": r["location"],
        "domain": r["domain"],
        "route": r["route"],
        "condition": diagnosis_service.clean_label(r["condition"]),
        "certainty": r["certainty"],
        "confidence": r["final_confidence"] or 0.0,
        "visual_confidence": r["visual_confidence"] or 0.0,
        "healthy": _is_healthy(r["condition"]),
        "summary": r["summary"] or "",
        "farmer_text": r["farmer_text"] or "",
        "has_sensor": bool(r["sensor_json"]),
        "has_image": diagnosis_service.image_path_for(r["observation_id"]) is not None,
    }


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@router.get("/overview")
def overview(days: int = Query(30, ge=1, le=365), _: str = Depends(current_admin)) -> dict:
    checks = _all_checks()
    farmers = _farmers()
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    prev_since = since - timedelta(days=days)

    in_window = [c for c in checks if _parse(c["created_at"]) >= since]
    in_prev = [c for c in checks if prev_since <= _parse(c["created_at"]) < since]

    def summarize(rows: list[dict]) -> dict:
        total = len(rows)
        healthy = sum(1 for r in rows if _is_healthy(r["condition"]))
        confs = [r["final_confidence"] or 0.0 for r in rows]
        return {
            "checks": total,
            "crop": sum(1 for r in rows if r["domain"] == "crop"),
            "livestock": sum(1 for r in rows if r["domain"] == "livestock"),
            "healthy": healthy,
            "attention": total - healthy,
            "local": sum(1 for r in rows if r["route"] == "local"),
            "cloud": sum(1 for r in rows if r["route"] == "cloud"),
            "avg_confidence": round(sum(confs) / total, 4) if total else 0.0,
            "low_confidence": sum(1 for c in confs if c < 0.5),
            "active_farmers": len({r["farm_id"] for r in rows}),
            "with_notes": sum(1 for r in rows if (r["farmer_text"] or "").strip()),
            "with_sensor": sum(1 for r in rows if r["sensor_json"]),
        }

    # Daily series (UTC dates), zero-filled so the chart has no gaps.
    daily: dict[str, Counter] = defaultdict(Counter)
    for c in in_window:
        day = _parse(c["created_at"]).date().isoformat()
        daily[day][c["domain"]] += 1
        daily[day]["attention"] += 0 if _is_healthy(c["condition"]) else 1
    series = []
    for i in range(days - 1, -1, -1):
        d = (now - timedelta(days=i)).date().isoformat()
        series.append({"date": d, "crop": daily[d]["crop"], "livestock": daily[d]["livestock"], "attention": daily[d]["attention"]})

    cond_stats: dict[str, dict] = {}
    for c in in_window:
        name = diagnosis_service.clean_label(c["condition"])
        s = cond_stats.setdefault(name, {"condition": name, "domain": c["domain"], "count": 0, "conf_sum": 0.0, "cloud": 0})
        s["count"] += 1
        s["conf_sum"] += c["final_confidence"] or 0.0
        s["cloud"] += c["route"] == "cloud"
    top_conditions = sorted(
        ({"condition": s["condition"], "domain": s["domain"], "count": s["count"],
          "avg_confidence": round(s["conf_sum"] / s["count"], 4), "cloud": s["cloud"],
          "healthy": _is_healthy(s["condition"])} for s in cond_stats.values()),
        key=lambda x: -x["count"],
    )[:10]

    region_checks = Counter((c["location"] or "Unknown") for c in in_window)
    region_attention = Counter((c["location"] or "Unknown") for c in in_window if not _is_healthy(c["condition"]))
    region_farmers = Counter((f["location"] or "Unknown") for f in farmers)
    regions = sorted(
        ({"region": r, "farmers": region_farmers.get(r, 0), "checks": region_checks.get(r, 0),
          "attention": region_attention.get(r, 0)} for r in set(region_checks) | set(region_farmers)),
        key=lambda x: (-x["checks"], -x["farmers"]),
    )

    buckets = [0] * 10
    for c in in_window:
        buckets[min(9, int((c["final_confidence"] or 0.0) * 10))] += 1

    hours = [0] * 24
    for c in in_window:
        # IST view of activity: when do farmers actually use the app?
        hours[(_parse(c["created_at"]) + timedelta(hours=5, minutes=30)).hour] += 1

    new_farmers = sum(1 for f in farmers if f["created_at"] and _parse(f["created_at"]) >= since)

    # Outbreak watch: an attention-worthy condition seen 3+ times in the last 7 days in one region.
    week = now - timedelta(days=7)
    cluster = Counter(
        (diagnosis_service.clean_label(c["condition"]), c["location"] or "Unknown")
        for c in checks if _parse(c["created_at"]) >= week and not _is_healthy(c["condition"])
    )
    alerts = [{"condition": k[0], "region": k[1], "count": v} for k, v in cluster.most_common() if v >= 3]

    return {
        "days": days,
        "generated_at": now.isoformat(),
        "totals": {"farmers": len(farmers), "new_farmers": new_farmers, "all_time_checks": len(checks)},
        "current": summarize(in_window),
        "previous": summarize(in_prev),
        "daily": series,
        "top_conditions": top_conditions,
        "regions": regions,
        "confidence_buckets": buckets,
        "hours_ist": hours,
        "alerts": alerts,
        "recent": [_check_row(c) for c in checks[:8]],
    }


# ---------------------------------------------------------------------------
# Browsing
# ---------------------------------------------------------------------------

@router.get("/farmers")
def farmers(_: str = Depends(current_admin)) -> list[dict]:
    checks = _all_checks()
    per_farm: dict[str, list[dict]] = defaultdict(list)
    for c in checks:
        per_farm[c["farm_id"]].append(c)
    out = []
    for f in _farmers():
        rows = per_farm.get(f["farm_id"], [])
        out.append({
            "farm_id": f["farm_id"],
            "name": f["farmer_name"] or "—",
            "phone": _mask(f["phone"]),
            "region": f["location"],
            "created_at": f["created_at"],
            "checks": len(rows),
            "crop": sum(1 for r in rows if r["domain"] == "crop"),
            "livestock": sum(1 for r in rows if r["domain"] == "livestock"),
            "attention": sum(1 for r in rows if not _is_healthy(r["condition"])),
            "last_check_at": rows[0]["created_at"] if rows else None,
        })
    return sorted(out, key=lambda x: (x["last_check_at"] or "", x["created_at"] or ""), reverse=True)


@router.get("/farmers/{farm_id}")
def farmer_detail(farm_id: str, _: str = Depends(current_admin)) -> dict:
    f = next((x for x in _farmers() if x["farm_id"] == farm_id), None)
    if not f:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Farmer not found.")
    rows = [c for c in _all_checks() if c["farm_id"] == farm_id]
    return {
        "farm_id": farm_id, "name": f["farmer_name"] or "—", "phone": _mask(f["phone"]),
        "region": f["location"], "created_at": f["created_at"],
        "checks": [_check_row(r) for r in rows],
    }


@router.get("/diagnoses")
def diagnoses(_: str = Depends(current_admin)) -> list[dict]:
    return [_check_row(c) for c in _all_checks()]


@router.get("/diagnoses/{observation_id}")
def diagnosis_detail(observation_id: int, _: str = Depends(current_admin)) -> dict:
    row = next((c for c in _all_checks() if c["observation_id"] == observation_id), None)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found.")
    detail = diagnosis_service.load_detail(row["farm_id"], observation_id) or {}
    return {**detail, "farmer_name": row["farmer_name"] or "—", "region": row["location"], "farm_id": row["farm_id"]}


@router.get("/diagnoses/{observation_id}/image")
def diagnosis_image(observation_id: int, token: str = Query(...)) -> FileResponse:
    claims = read_token(token)
    if not claims or claims.get("typ") != "admin":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized.")
    path = diagnosis_service.image_path_for(observation_id)
    if not path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No photo for this record.")
    return FileResponse(path)


@router.get("/export.csv")
def export_csv(_: str = Depends(current_admin)) -> StreamingResponse:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "created_at_utc", "farmer", "region", "domain", "route", "condition", "certainty",
                "confidence", "visual_confidence", "healthy", "farmer_text", "summary"])
    for c in _all_checks():
        r = _check_row(c)
        w.writerow([r["id"], r["created_at"], r["farmer_name"], r["region"] or "", r["domain"], r["route"],
                    r["condition"], r["certainty"] or "", f"{r['confidence']:.4f}", f"{r['visual_confidence']:.4f}",
                    r["healthy"], r["farmer_text"], r["summary"]])
    return StreamingResponse(
        iter([buf.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="agrivision-checks-{datetime.now():%Y%m%d}.csv"'},
    )


# ---------------------------------------------------------------------------
# System health
# ---------------------------------------------------------------------------

def _dir_stats(path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    files = [p for p in path.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


def _llm_status() -> dict:
    backend = os.environ.get("ADVISORY_BACKEND", "gemini").lower()
    url = os.environ.get("LOCAL_LLM_URL", "").rstrip("/")
    info = {"backend": backend, "model": os.environ.get("LOCAL_LLM_MODEL", ""), "configured": bool(url),
            "reachable": None, "latency_ms": None}
    if backend != "local_llm" or not url:
        return info
    req = urllib.request.Request(f"{url}/models")
    key = os.environ.get("LOCAL_LLM_API_KEY")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:  # noqa: S310 - configured endpoint
            info["reachable"] = resp.status == 200
    except Exception:  # noqa: BLE001 - any failure means "not reachable"
        info["reachable"] = False
    info["latency_ms"] = round((time.perf_counter() - started) * 1000)
    return info


@router.get("/system")
def system(_: str = Depends(current_admin)) -> dict:
    models_dir = PROJECT_ROOT / "models_cache"
    model_parts = {
        "crop_model": models_dir / "crop_model",
        "livestock_model (CLIP router)": models_dir / "livestock_model",
        "moe/crop_row": models_dir / "moe" / "crop_row",
        "moe/crop_perennial": models_dir / "moe" / "crop_perennial",
        "moe/livestock_fmd": models_dir / "moe" / "livestock_fmd",
        "moe/livestock_lsd": models_dir / "moe" / "livestock_lsd",
    }
    models = []
    for name, path in model_parts.items():
        _, size = _dir_stats(path)
        models.append({"name": name, "present": path.exists() and size > 0, "size_bytes": size})

    uploads_n, uploads_bytes = _dir_stats(settings.upload_dir)
    db = farm_memory.DEFAULT_DB_PATH
    gemini_ready = (
        os.environ.get("GEMINI_ENABLED", "false").lower() == "true"
        and bool(os.environ.get("GEMINI_API_KEY"))
        and os.environ.get("GEMINI_API_KEY") != "your_gemini_api_key_here"
    )
    return {
        "api": {"version": "1.0.0", "uptime_s": round(time.time() - _STARTED_AT), "python": platform.python_version(),
                "platform": f"{platform.system()} {platform.machine()}"},
        "vision": {"expert_mode": settings.expert_mode,
                   "moe_enabled": os.environ.get("AGRIVISION_MOE_ENABLED", "auto"),
                   "moe_routing": " / ".join(f"{d} {r}" for d, r in zone1_config.MOE_ROUTING_BY_DOMAIN.items())},
        "llm": _llm_status(),
        "gemini_ready": gemini_ready,
        "rag_backend": os.environ.get("RAG_BACKEND", "auto"),
        "weather_enabled": os.environ.get("WEATHER_ENABLED", "false").lower() == "true",
        "translation": translation.status(),
        "demo_otp": settings.demo_otp,
        "default_admin_password": settings.admin_password == "agrivision-admin",
        "storage": {"db_bytes": db.stat().st_size if db.exists() else 0, "uploads_files": uploads_n,
                    "uploads_bytes": uploads_bytes},
        "models": models,
    }
