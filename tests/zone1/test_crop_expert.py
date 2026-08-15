from src.zone1_edge.experts import crop_expert


def test_crop_expert_returns_contract_shape(synthetic_crop_image):
    out = crop_expert.run(synthetic_crop_image, mode="mock")
    assert out["domain"] == "crop"
    assert out["input_type"] == "image"
    assert isinstance(out["prediction"], str)
    assert isinstance(out["confidence"], float)
    assert 0.0 <= out["confidence"] <= 1.0
    assert isinstance(out["top_k"], list)
    assert len(out["top_k"]) >= 1
    for label, prob in out["top_k"]:
        assert isinstance(label, str)
        assert isinstance(prob, float)


def test_crop_expert_is_deterministic(synthetic_crop_image):
    out1 = crop_expert.run(synthetic_crop_image, mode="mock")
    out2 = crop_expert.run(synthetic_crop_image, mode="mock")
    assert out1["prediction"] == out2["prediction"]
    assert out1["confidence"] == out2["confidence"]


def test_crop_expert_top_k_sorted_descending(synthetic_crop_image):
    out = crop_expert.run(synthetic_crop_image, mode="mock")
    probs = [p for _, p in out["top_k"]]
    assert probs == sorted(probs, reverse=True)
