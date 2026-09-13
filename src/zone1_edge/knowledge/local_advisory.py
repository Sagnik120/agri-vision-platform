"""
local_advisory.py — Person A, Zone 1 (Hour 5:45-6:15 of the plan).

Looks up knowledge/local_advisories.json by condition name (the `prediction`
field from fusion/gate output). This is the fully-offline "local" advisory
path — used whenever confidence_gate.py sets route == 'local'.

Returns:
    {"condition": str, "summary": str, "actions": [str,...], "warning": str,
     "source": "local_offline"}
"""

from __future__ import annotations

import json
from pathlib import Path

from src.zone1_edge import config

_ADVISORY_PATH = config.KNOWLEDGE_DIR / "local_advisories.json"

_FALLBACK_ADVISORY = {
    "condition_name": "Unknown",
    "description": "No local advisory entry found for this condition.",
    "common_symptoms": [],
    "immediate_action": "Escalate to cloud advisory (Person B) for a knowledge-base-grounded answer.",
    "preventive_action": "Consult a local agriculture/veterinary officer if symptoms worsen.",
    "escalation_trigger": "This condition is not yet in the offline knowledge base.",
    "safety_note": "Unknown.",
    "reference": "Fallback"
}


def _load_db() -> dict:
    with open(_ADVISORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_advisory(condition: str) -> dict:
    db = _load_db()
    
    # Normalize condition string to match DB keys
    # e.g. "Potato___Early_Blight" -> "potato_early_blight"
    normalized_condition = condition.lower().replace("___", "_").replace("__", "_")
    
    entry = db.get(normalized_condition, _FALLBACK_ADVISORY)
    
    # Safely handle legacy entries during transition
    return {
        "condition": condition,
        "condition_name": entry.get("condition_name", normalized_condition.replace("_", " ").title()),
        "summary": entry.get("description", entry.get("summary", "No description available.")),
        "actions": [entry.get("immediate_action", ""), entry.get("preventive_action", "")] if "immediate_action" in entry else entry.get("actions", []),
        "warning": entry.get("escalation_trigger", entry.get("warning", "")),
        "source": "local_offline",
        "reference": entry.get("reference", "Fallback"),
        "safety_note": entry.get("safety_note", ""),
    }


if __name__ == "__main__":
    import sys

    cond = sys.argv[1] if len(sys.argv) > 1 else "tomato_early_blight"
    print(json.dumps(get_advisory(cond), indent=2))
