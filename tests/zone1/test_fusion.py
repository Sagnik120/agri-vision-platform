from src.zone1_edge.multimodal import fusion


def _image_out(pred="tomato_early_blight", conf=0.70):
    return {"domain": "crop", "input_type": "image", "prediction": pred,
            "confidence": conf, "top_k": [[pred, conf]]}


def test_fusion_contract_shape():
    out = fusion.fuse(_image_out())
    assert set(out.keys()) == {
        "prediction", "visual_confidence", "text_support",
        "sensor_support", "evidence_agreement", "final_confidence", "route", "sensor_data"
    }


def test_text_support_increases_confidence():
    base = fusion.fuse(_image_out(conf=0.70))
    supported = fusion.fuse(_image_out(conf=0.70),
                             {"symptoms": ["brown_spots"], "crop": "tomato", "severity_hint": "low"})
    assert supported["final_confidence"] > base["final_confidence"]
    assert supported["text_support"] is True


def test_text_conflict_decreases_confidence():
    conflicting = fusion.fuse(
        _image_out(pred="tomato_healthy", conf=0.70),
        {"symptoms": ["brown_spots", "wilting"], "crop": "tomato", "severity_hint": "high"},
    )
    assert conflicting["final_confidence"] < 0.70
    assert conflicting["text_support"] is False


def test_confidence_capped_at_099():
    out = fusion.fuse(
        _image_out(conf=0.98),
        {"symptoms": ["brown_spots"], "crop": "tomato", "severity_hint": "high"},
        {"domain": "livestock", "temperature": 39.0, "activity": "normal",
         "feed_intake": "normal", "anomaly": False},
    )
    assert out["final_confidence"] <= 0.99


def test_confidence_floor_at_001():
    out = fusion.fuse(
        _image_out(pred="tomato_healthy", conf=0.05),
        {"symptoms": ["brown_spots", "wilting", "black_spots"], "crop": "tomato", "severity_hint": "high"},
    )
    assert out["final_confidence"] >= 0.01


def test_sensor_support_and_conflict():
    supported = fusion.fuse(
        {"domain": "livestock", "input_type": "image", "prediction": "lumpy_skin_disease",
         "confidence": 0.6, "top_k": []},
        sensor_output=None,
    )
    assert supported["sensor_support"] is None  # no sensor passed

    with_sensor = fusion.fuse(
        {"domain": "livestock", "input_type": "image", "prediction": "lumpy_skin_disease",
         "confidence": 0.6, "top_k": []},
        sensor_output={"domain": "livestock", "temperature": 40.0, "activity": "low",
                        "feed_intake": "low", "anomaly": True},
    )
    assert with_sensor["sensor_support"] is True
    assert with_sensor["final_confidence"] > 0.6

from src.zone1_edge.multimodal.text_evidence import extract_symptoms

def test_expanded_symptom_dictionary_supports():
    symptoms = extract_symptoms("मेरी फसल पर dhhabba और peela marks हैं")
    out = fusion.fuse(_image_out(pred="tomato_early_blight", conf=0.70), {"symptoms": symptoms})
    assert out["text_support"] is True
    assert out["final_confidence"] > 0.70

def test_expanded_symptom_dictionary_conflicts():
    symptoms = extract_symptoms("गाय langda चल रही है और fever है")
    # if image is healthy but symptoms exist
    out = fusion.fuse(
        _image_out(pred="healthy", conf=0.8),
        {"symptoms": symptoms}
    )
    assert out["text_support"] is False
    assert out["final_confidence"] < 0.8

def test_expanded_symptom_dictionary_multiple():
    symptoms = extract_symptoms("pests on leaves and sookhna")
    assert "insects" in symptoms
    assert "drying" in symptoms

def test_device_tier_resilience(monkeypatch):
    from src.zone1_edge import config
    monkeypatch.setattr(config, "get_device_tier", lambda: "low")
    symptoms = extract_symptoms("unrelated text")
    out = fusion.fuse(_image_out(pred="tomato_early_blight", conf=0.70), {"symptoms": ["fake_symptom"]})
    # normally this would be text_support=False and confidence=0.5
    # with tier="low", it should be text_support=False but wait, the new logic returns None
    assert out["text_support"] is None # text_agree is None for low-tier mismatch
    assert out["final_confidence"] == 0.70 # No penalty applied
