from src.zone1_edge.multimodal import fusion


def _image_out(pred="tomato_early_blight", conf=0.70):
    return {"domain": "crop", "input_type": "image", "prediction": pred,
            "confidence": conf, "top_k": [[pred, conf]]}


def test_fusion_contract_shape():
    out = fusion.fuse(_image_out())
    assert set(out.keys()) == {
        "prediction", "visual_confidence", "text_support",
        "sensor_support", "evidence_agreement", "final_confidence", "route",
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
