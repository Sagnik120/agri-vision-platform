import pytest
from src.zone2_cloud.gemini.validator import validate_advisory

def test_validate_clean():
    resp = {
        "diagnosis": {"condition": "Tomato Early Blight", "certainty": "possible"},
        "advisory": {"summary": "Use copper spray", "actions": [], "warning": ""},
        "expert_consultation_recommended": False,
        "cited_knowledge": []
    }
    is_valid, reasons = validate_advisory(resp, ["Tomato Early blight is bad"], {})
    assert is_valid
    assert not reasons

def test_validate_ungrounded():
    resp = {
        "diagnosis": {"condition": "Alien Virus", "certainty": "possible"},
        "advisory": {"summary": "Panic", "actions": [], "warning": ""},
        "expert_consultation_recommended": True,
        "cited_knowledge": []
    }
    is_valid, reasons = validate_advisory(resp, ["Just normal plants here"], {})
    assert not is_valid
    assert "alien virus" in reasons[0]

def test_validate_drug_dosage():
    resp = {
        "diagnosis": {"condition": "Lumpy Skin Disease", "certainty": "possible"},
        "advisory": {"summary": "Give 50 mg antibiotics", "actions": [], "warning": ""},
        "expert_consultation_recommended": True,
        "cited_knowledge": []
    }
    is_valid, reasons = validate_advisory(resp, ["Lumpy Skin Disease is viral"], {})
    assert not is_valid
    assert "Safety violation" in reasons[0]
