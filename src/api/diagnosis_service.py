"""
Orchestrates one diagnosis exactly like the Streamlit shell does
(Zone 1 -> confidence gate -> optional Zone 2 escalation -> Zone 3 persistence),
but yields progress events so the web UI can show each real stage live.

Each saved diagnosis also gets a JSON sidecar + the uploaded photo under
results/api_uploads/, because the SQLite schema only keeps the summary fields.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterator
from pathlib import Path

from src.api.config import settings
from src.api.repository import get_history_item

_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def clean_label(label: str | None) -> str:
    if not label:
        return "Unknown"
    return " ".join(label.replace("___", " ").replace("_", " ").split()).strip() or "Unknown"


def _jsonable(obj):
    """Round-trip through JSON so numpy scalars and other odd types become plain values."""
    return json.loads(json.dumps(obj, default=lambda o: float(o) if hasattr(o, "__float__") else str(o)))


def sidecar_path(observation_id: int) -> Path:
    return settings.upload_dir / f"{observation_id}.json"


def image_path_for(observation_id: int) -> Path | None:
    for ext in _IMAGE_EXTS:
        p = settings.upload_dir / f"{observation_id}{ext}"
        if p.exists():
            return p
    return None


def _stage(stage: str, status: str, **extra) -> dict:
    return {"type": "stage", "stage": stage, "status": status, **extra}


def run(
    farm_id: str,
    image_path: str,
    image_ext: str,
    domain: str,
    farmer_text: str,
    sensor_reading: dict | None,
    region: str | None,
    season: str | None,
) -> Iterator[dict]:
    # Heavy imports stay lazy so the API boots instantly and /health works without models.
    from src.zone1_edge.pipeline import build_cloud_payload_stub, run_zone1_pipeline
    from src.zone2_cloud import advisory_service
    from src.zone2_cloud.rag import retriever
    from src.zone3_memory.db import farm_memory

    yield _stage("vision", "active")
    result = run_zone1_pipeline(
        domain, image_path,
        farmer_text=farmer_text or None,
        sensor_reading=sensor_reading,
        mode=settings.expert_mode,
        region=region, season=season,
    )
    gate = result.get("gate", {})

    if gate.get("route") == "reject":
        yield _stage("vision", "error")
        yield {"type": "rejected", "reason": gate.get("reason") or "Please retake the photo."}
        return

    image_output = result.get("image_output") or {}
    actual_domain = image_output.get("domain", domain if domain in ("crop", "livestock") else "crop")
    yield _stage("vision", "done", domain=actual_domain, prediction=clean_label(gate.get("prediction")))

    route = gate.get("route", "local")
    yield _stage("gate", "done", route=route, confidence=gate.get("final_confidence", 0.0))

    obs_id = farm_memory.save_observation(
        farm_id=farm_id,
        domain=actual_domain,
        image_prediction=gate.get("prediction", "unknown"),
        visual_confidence=gate.get("visual_confidence", 0.0),
        farmer_text=farmer_text or "",
        sensor_json=json.dumps(result.get("sensor_output") or {}),
        route=route,
    )

    extra: dict = {}
    if route == "local":
        adv = result.get("local_advisory") or {}
        condition, certainty = gate.get("prediction", "Unknown"), "possible"
        source = "local_offline"
    else:
        yield _stage("knowledge", "active")
        rag_knowledge = retriever.retrieve(f"{gate.get('prediction', '')} {farmer_text or ''}")
        farm_hist = farm_memory.format_farm_history(farm_memory.get_farm_history_records(farm_id))
        yield _stage("knowledge", "done")

        yield _stage("cloud", "active")
        payload = build_cloud_payload_stub(result)
        payload.update(farmer_text=farmer_text or "", farm_history=farm_hist,
                       retrieved_knowledge=rag_knowledge, image_path=image_path)
        cloud = advisory_service.generate_advisory(payload)
        yield _stage("cloud", "done")

        diag, adv = cloud.get("diagnosis", {}) or {}, cloud.get("advisory", {}) or {}
        condition, certainty = diag.get("condition", "Unknown"), diag.get("certainty", "possible")
        source = "cloud_gemini"
        extra = {
            "expert_consultation_recommended": bool(cloud.get("expert_consultation_recommended")),
            "citations": cloud.get("cited_knowledge") or [],
            "citation_check": cloud.get("_citation_check") or {},
            "weather": cloud.get("_weather_used"),
            "advisory_backend": cloud.get("_backend"),
        }

    diag_id = farm_memory.save_diagnosis(obs_id, condition=condition, certainty=certainty,
                                         final_confidence=gate.get("final_confidence", 0.0))
    farm_memory.save_advisory(diag_id, source=source, summary=adv.get("summary", ""),
                              actions=adv.get("actions", []), warning=adv.get("warning", ""))

    expl = result.get("explainability") or {}
    ctx = result.get("context") or {}
    detail = {
        "id": obs_id,
        "domain": actual_domain,
        "route": route,
        "prediction": gate.get("prediction"),
        "condition": clean_label(condition),
        "certainty": certainty,
        "confidence": gate.get("final_confidence", 0.0),
        "visual_confidence": gate.get("visual_confidence", 0.0),
        "evidence_agreement": gate.get("evidence_agreement"),
        "summary": adv.get("summary", ""),
        "actions": [a for a in adv.get("actions", []) if a],
        "warning": adv.get("warning", ""),
        "safety_note": adv.get("safety_note", ""),
        "top_predictions": [
            {"label": clean_label(v.get("label")), "confidence": v.get("confidence", 0.0)}
            for _, v in sorted(expl.get("top3", {}).items())
        ],
        "reason": expl.get("reason_string", ""),
        "context": {"season": ctx.get("season"), "region": ctx.get("region"), "note": adv.get("context_note")},
        "quality_flag": (result.get("quality") or {}).get("quality_flag", "ok"),
        "vision_backend": image_output.get("_backend", "unknown"),
        "moe": image_output.get("_moe"),
        "farmer_text": farmer_text or "",
        "sensor": result.get("sensor_output"),
        "expert_consultation_recommended": False,
        "citations": [],
        **extra,
    }
    detail = _jsonable(detail)

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(image_path, settings.upload_dir / f"{obs_id}{image_ext}")
    sidecar_path(obs_id).write_text(json.dumps(detail, ensure_ascii=False, indent=2))

    yield {"type": "result", "data": load_detail(farm_id, obs_id)}


def load_detail(farm_id: str, observation_id: int) -> dict | None:
    row = get_history_item(farm_id, observation_id)
    if not row:
        return None
    side = sidecar_path(observation_id)
    if side.exists():
        detail = json.loads(side.read_text())
    else:
        # Records created before the API existed (e.g. via Streamlit) have no sidecar.
        detail = {
            "id": observation_id, "domain": row["domain"], "route": row["route"],
            "prediction": row["image_prediction"], "condition": clean_label(row["condition"]),
            "certainty": row["certainty"], "confidence": row["final_confidence"] or 0.0,
            "visual_confidence": row["visual_confidence"] or 0.0, "summary": row["summary"] or "",
            "actions": [], "warning": "", "top_predictions": [], "citations": [],
            "farmer_text": row["farmer_text"] or "", "context": {},
        }
    detail["created_at"] = row["created_at"]
    detail["has_image"] = image_path_for(observation_id) is not None
    return detail
