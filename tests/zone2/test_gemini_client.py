import pytest
from src.zone2_cloud.gemini.gemini_client import build_prompt, strip_pii

def test_gemini_prompt_builder():
    payload = {
        "farmer_id": "f-123",
        "phone": "555-0000",
        "farmer_name": "John",
        "advisory_tier": "possible",
        "domain": "crop"
    }
    prompt = build_prompt(payload)
    
    # Assert PII stripped
    assert "555-0000" not in prompt
    assert "John" not in prompt
    
    # Assert contract fields present
    assert "f-123" in prompt
    assert "possible" in prompt
    
    # Assert prompt instructions
    assert "STRICT RULES" in prompt
