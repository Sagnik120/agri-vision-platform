"""
kb_loader.py - Person B Implementation
"""

import json
from pathlib import Path

def get_safety_critical_conditions() -> set[str]:
    """
    Reads `is_safety_critical: bool` from knowledge base entries and returns
    the set of condition keys flagged true.
    """
    kb_path = Path(__file__).parent / "local_advisories.json"
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        critical_set = set()
        for key, entry in data.items():
            if entry.get("is_safety_critical", False):
                critical_set.add(key)
        return critical_set
    except Exception as e:
        # Fallback for safety if file is missing/broken
        print(f"Warning: Failed to load local advisories: {e}")
        return {"foot_and_mouth_disease", "lumpy_skin_disease", "potato_late_blight", "tomato_late_blight"}
