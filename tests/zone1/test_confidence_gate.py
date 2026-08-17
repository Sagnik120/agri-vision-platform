from src.zone1_edge.multimodal import confidence_gate


def _fusion(conf=0.9, agreement="high"):
    return {"prediction": "tomato_early_blight", "visual_confidence": 0.8,
            "text_support": True, "sensor_support": None,
            "evidence_agreement": agreement, "final_confidence": conf, "route": "local"}


def test_high_confidence_high_agreement_routes_local():
    out = confidence_gate.decide_route(_fusion(conf=0.9, agreement="high"), input_quality_ok=True)
    assert out["route"] == "local"


def test_low_confidence_routes_cloud():
    out = confidence_gate.decide_route(_fusion(conf=0.5, agreement="high"), input_quality_ok=True)
    assert out["route"] == "cloud"


def test_low_evidence_agreement_routes_cloud_even_if_confident():
    out = confidence_gate.decide_route(_fusion(conf=0.95, agreement="low"), input_quality_ok=True)
    assert out["route"] == "cloud"


def test_bad_input_quality_forces_cloud():
    out = confidence_gate.decide_route(_fusion(conf=0.95, agreement="high"), input_quality_ok=False)
    assert out["route"] == "cloud"


def test_preserves_contract_5_keys():
    out = confidence_gate.decide_route(_fusion())
    for key in ["prediction", "visual_confidence", "text_support", "sensor_support",
                "evidence_agreement", "final_confidence", "route"]:
        assert key in out

def test_safety_critical_routes_cloud(monkeypatch):
    from src.zone1_edge.multimodal import confidence_gate
    # Mock kb_loader
    monkeypatch.setattr(confidence_gate, "get_safety_critical_conditions", lambda: {"tomato_early_blight"})
    # Even with high confidence (0.9 > 0.85), safety critical should ALWAYS route cloud
    # Wait, the instructions say:
    # "Cloud if confidence < threshold, OR if safety critical (always double check), OR if text_support is False (conflicting evidence)."
    # And my logic implemented exactly that: `not is_critical`.
    out = confidence_gate.decide_route(_fusion(conf=0.9, agreement="high"), input_quality_ok=True)
    assert out["route"] == "cloud"
    assert "Safety critical prediction" in out["threshold_reason"]

def test_dynamic_threshold(monkeypatch):
    from src.zone1_edge.multimodal import confidence_gate
    # If prediction is safety critical, threshold is 0.85
    monkeypatch.setattr(confidence_gate, "get_safety_critical_conditions", lambda: {"tomato_early_blight"})
    out = confidence_gate.decide_route(_fusion(conf=0.8, agreement="high"), input_quality_ok=True)
    assert out["route"] == "cloud"
    # Should say Confidence 0.80 below threshold 0.85
    assert any("below threshold 0.85" in r for r in out["threshold_reason"])

def test_text_support_conflict_routes_cloud():
    # text_support = False
    data = _fusion(conf=0.9, agreement="high")
    data["text_support"] = False
    out = confidence_gate.decide_route(data, input_quality_ok=True)
    assert out["route"] == "cloud"
    assert "Farmer symptoms conflict" in out["threshold_reason"]
