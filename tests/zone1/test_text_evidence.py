from src.zone1_edge.multimodal import text_evidence


def test_hindi_symptom_extraction():
    out = text_evidence.run({"text": "पत्तियों पर भूरे धब्बे और पीली पत्तियां हैं", "language": "hi", "confidence": None})
    assert "brown_spots" in out["symptoms"]
    assert "yellow_leaves" in out["symptoms"]
    assert set(out.keys()) == {"symptoms", "crop", "severity_hint"}


def test_english_symptom_extraction():
    out = text_evidence.run({"text": "There are brown spots and wilting on the tomato", "language": "hi", "confidence": None})
    assert "brown_spots" in out["symptoms"]
    assert "wilting" in out["symptoms"]
    assert out["crop"] == "tomato"


def test_crop_detection():
    out = text_evidence.run({"text": "मक्का में कीड़े हैं", "language": "hi", "confidence": None})
    assert out["crop"] == "maize"
    assert "insects" in out["symptoms"]


def test_no_symptoms_found():
    out = text_evidence.run({"text": "यह एक सामान्य वाक्य है", "language": "hi", "confidence": None})
    assert out["symptoms"] == []
    assert out["crop"] == "unknown"
    assert out["severity_hint"] == "low"


def test_severity_high_detection():
    out = text_evidence.run({"text": "पूरी फसल गंभीर रूप से खराब हो गई", "language": "hi", "confidence": None})
    assert out["severity_hint"] == "high"


def test_accepts_raw_string_too():
    out = text_evidence.run("brown spots on tomato")
    assert "brown_spots" in out["symptoms"]
