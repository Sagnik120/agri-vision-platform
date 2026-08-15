"""
text_evidence.py — Person A, Zone 1 (Hour 2:30-3:15 of the plan).

Rule-based symptom extractor. NO MODEL — deterministic Hindi + English
keyword -> symptom dictionary. Consumes Person B's ASR output
(contract.md #2: {"text": str, "language":"hi", "confidence": null})
and produces contract.md #3:

    {"symptoms": [str,...], "crop": str, "severity_hint": str}

Usage:
    python -m src.zone1_edge.multimodal.text_evidence "पत्तियों पर भूरे धब्बे हैं"
"""

from __future__ import annotations

import json
import re
import sys
from typing import Dict, List

# Hindi + English keyword -> canonical symptom. Extend freely; deterministic
# substring match only, case-insensitive for English.
SYMPTOM_KEYWORDS: Dict[str, str] = {
    "भूरे धब्बे": "brown_spots",
    "brown spots": "brown_spots",
    "पीली पत्तियां": "yellow_leaves",
    "पीली पत्ती": "yellow_leaves",
    "yellow leaves": "yellow_leaves",
    "सफेद पाउडर": "white_powder",
    "white powder": "white_powder",
    "पत्तियां मुड़": "leaf_curl",
    "leaf curl": "leaf_curl",
    "curling leaves": "leaf_curl",
    "कीड़े": "insects",
    "insects": "insects",
    "pests": "insects",
    "मुरझा": "wilting",
    "wilting": "wilting",
    "काले धब्बे": "black_spots",
    "black spots": "black_spots",
    "सूखना": "drying",
    "drying": "drying",
    "बुखार": "fever",
    "fever": "fever",
    "लंगड़ा": "limping",
    "limping": "limping",
    "सूजन": "swelling",
    "swelling": "swelling",
    "भूख नहीं": "loss_of_appetite",
    "not eating": "loss_of_appetite",
    "loss of appetite": "loss_of_appetite",
}

# Crop keyword dictionary (Hindi + English) -> canonical crop name.
CROP_KEYWORDS: Dict[str, str] = {
    "टमाटर": "tomato",
    "tomato": "tomato",
    "आलू": "potato",
    "potato": "potato",
    "मक्का": "maize",
    "maize": "maize",
    "corn": "maize",
    "मिर्च": "pepper",
    "pepper": "pepper",
    "गाय": "cattle",
    "cattle": "cattle",
    "cow": "cattle",
}

SEVERITY_KEYWORDS = {
    "high": ["बहुत", "गंभीर", "severe", "very", "puri fasal", "पूरी फसल"],
    "medium": ["कुछ", "some", "moderate", "थोड़ा"],
}


def extract_symptoms(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for kw, symptom in SYMPTOM_KEYWORDS.items():
        if kw.lower() in text_lower and symptom not in found:
            found.append(symptom)
    return found


def extract_crop(text: str) -> str:
    text_lower = text.lower()
    for kw, crop in CROP_KEYWORDS.items():
        if kw.lower() in text_lower:
            return crop
    return "unknown"


def extract_severity(text: str) -> str:
    text_lower = text.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return level
    return "low"


def run(asr_output: dict) -> dict:
    """
    Consumes contract #2 (Person B ASR output) and returns contract #3.
    Accepts either a dict {"text":..., "language":..., "confidence":...}
    or a raw string for convenience/testing.
    """
    if isinstance(asr_output, dict):
        text = asr_output.get("text", "")
    else:
        text = str(asr_output)

    return {
        "symptoms": extract_symptoms(text),
        "crop": extract_crop(text),
        "severity_hint": extract_severity(text),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python -m src.zone1_edge.multimodal.text_evidence "<hindi or english text>"')
        sys.exit(1)
    out = run({"text": sys.argv[1], "language": "hi", "confidence": None})
    print(json.dumps(out, indent=2, ensure_ascii=False))
