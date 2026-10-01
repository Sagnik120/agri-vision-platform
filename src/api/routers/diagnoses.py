"""Run a diagnosis (streamed NDJSON progress) and read the farm's history."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse

from src.api import diagnosis_service, repository, translation
from src.api.config import settings
from src.api.security import current_farm_id, read_token

router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])

_ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


@router.post("")
async def create_diagnosis(
    image: UploadFile = File(...),
    domain: str = Form("auto"),
    farmer_text: str = Form(""),
    sensor: str | None = Form(None, description='JSON: {"temperature": 38.5, "activity": "normal", "feed_intake": "normal"}'),
    season: str | None = Form(None),
    farm_id: str = Depends(current_farm_id),
) -> StreamingResponse:
    if domain not in ("auto", "crop", "livestock"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "domain must be auto, crop or livestock.")
    ext = _ALLOWED.get(image.content_type or "")
    if not ext:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Please upload a JPG, PNG or WebP photo.")
    data = await image.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Photo is larger than 10 MB.")

    sensor_reading = None
    if sensor:
        try:
            sensor_reading = json.loads(sensor)
        except json.JSONDecodeError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "sensor must be valid JSON.") from e

    # Keep the original (sanitized) filename like the Streamlit shell does:
    # the mock router's domain heuristic reads it.
    stem = re.sub(r"[^A-Za-z0-9_-]", "_", Path(image.filename or "photo").stem)[:60] or "photo"
    tmp_dir = tempfile.mkdtemp(prefix="agrivision_")
    tmp_path = os.path.join(tmp_dir, f"{stem}{ext}")
    with open(tmp_path, "wb") as f:
        f.write(data)

    region = (repository.get_profile(farm_id) or {}).get("region")

    def stream():
        try:
            for event in diagnosis_service.run(
                farm_id, tmp_path, ext, domain, farmer_text.strip(), sensor_reading, region, season or None
            ):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as e:  # noqa: BLE001 - surface any pipeline failure to the UI
            yield json.dumps({"type": "error", "message": f"Analysis failed: {type(e).__name__}"}) + "\n"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return StreamingResponse(stream(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@router.get("")
def list_diagnoses(farm_id: str = Depends(current_farm_id)) -> list[dict]:
    items = []
    for r in repository.list_history(farm_id):
        oid = r["observation_id"]
        items.append({
            "id": oid,
            "created_at": r["created_at"],
            "domain": r["domain"],
            "route": r["route"],
            "condition": diagnosis_service.clean_label(r["condition"]),
            "certainty": r["certainty"],
            "confidence": r["final_confidence"] or 0.0,
            "summary": r["summary"] or "",
            "farmer_text": r["farmer_text"] or "",
            "has_image": diagnosis_service.image_path_for(oid) is not None,
        })
    return items


@router.get("/{observation_id}")
def get_diagnosis(observation_id: int, farm_id: str = Depends(current_farm_id)) -> dict:
    detail = diagnosis_service.load_detail(farm_id, observation_id)
    if not detail:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found.")
    return detail


@router.get("/{observation_id}/translation")
def get_translation(observation_id: int, lang: str = Query("hi"), farm_id: str = Depends(current_farm_id)) -> dict:
    """Hindi version of the advisory text, translated once with IndicTrans2 and cached in the sidecar."""
    if lang != "hi":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Only Hindi is supported.")
    detail = diagnosis_service.load_detail(farm_id, observation_id)
    if not detail:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found.")
    cached = (detail.get("translations") or {}).get(lang)
    if cached:
        return {"available": True, **cached}

    fields = {
        "summary": detail.get("summary") or "",
        "warning": detail.get("warning") or "",
        "safety_note": detail.get("safety_note") or "",
        "context_note": (detail.get("context") or {}).get("note") or "",
    }
    actions = [a for a in detail.get("actions") or [] if a]
    texts = list(fields.values()) + actions
    out = translation.translate_many(texts)
    if out is None:
        return {"available": False, "reason": translation.status()["error"] or "Translation is turned off."}

    result = {**dict(zip(fields, out[: len(fields)])), "actions": out[len(fields):], "model": translation.MODEL_ID}
    side = diagnosis_service.sidecar_path(observation_id)
    if side.exists():  # cache so the next switch to Hindi is instant
        data = json.loads(side.read_text())
        data.setdefault("translations", {})[lang] = result
        side.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return {"available": True, **result}


@router.get("/{observation_id}/image")
def get_image(observation_id: int, token: str = Query(...)) -> FileResponse:
    # <img> tags cannot send an Authorization header, so the session token comes as a query param.
    claims = read_token(token)
    if not claims or claims.get("typ") != "session":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized.")
    if not repository.observation_belongs_to(claims["sub"], observation_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found.")
    path = diagnosis_service.image_path_for(observation_id)
    if not path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No photo for this record.")
    return FileResponse(path, headers={"Cache-Control": "private, max-age=86400"})
