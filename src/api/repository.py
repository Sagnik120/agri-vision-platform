"""
Read-side queries the API needs that zone3_memory does not expose yet.
Writes still go through zone3_memory.farm_memory / auth.
"""

from __future__ import annotations

import sqlite3

from src.zone3_memory.db import farm_memory


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(farm_memory.DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def phone_exists(phone: str) -> bool:
    with _connect() as conn:
        return conn.execute("SELECT 1 FROM farm WHERE phone = ?", (phone,)).fetchone() is not None


def get_profile(farm_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT farm_id, phone, farmer_name, location, created_at FROM farm WHERE farm_id = ?",
            (farm_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "farm_id": row["farm_id"],
        "phone": row["phone"],
        "name": row["farmer_name"],
        "region": row["location"],
        "created_at": row["created_at"],
    }


_HISTORY_SQL = """
    SELECT o.observation_id, o.created_at, o.domain, o.route, o.visual_confidence,
           o.image_prediction, o.farmer_text,
           d.condition, d.certainty, d.final_confidence,
           a.summary, a.source
    FROM observations o
    JOIN diagnoses d ON o.observation_id = d.observation_id
    LEFT JOIN advisories a ON d.diagnosis_id = a.diagnosis_id
    WHERE o.farm_id = ?
"""


def list_history(farm_id: str) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            _HISTORY_SQL + " ORDER BY o.created_at DESC, o.observation_id DESC", (farm_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_history_item(farm_id: str, observation_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(_HISTORY_SQL + " AND o.observation_id = ?", (farm_id, observation_id)).fetchone()
    return dict(row) if row else None


def observation_belongs_to(farm_id: str, observation_id: int) -> bool:
    with _connect() as conn:
        return conn.execute(
            "SELECT 1 FROM observations WHERE farm_id = ? AND observation_id = ?", (farm_id, observation_id)
        ).fetchone() is not None
