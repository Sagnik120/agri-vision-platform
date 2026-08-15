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
