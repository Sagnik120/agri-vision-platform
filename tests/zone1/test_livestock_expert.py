from src.zone1_edge.experts import livestock_expert


def test_livestock_expert_returns_contract_shape(synthetic_livestock_image):
    out = livestock_expert.run(synthetic_livestock_image, mode="mock")
    assert out["domain"] == "livestock"
    assert out["input_type"] == "image"
    assert isinstance(out["prediction"], str)
    assert 0.0 <= out["confidence"] <= 1.0
    assert isinstance(out["top_k"], list)


def test_livestock_expert_deterministic(synthetic_livestock_image):
    out1 = livestock_expert.run(synthetic_livestock_image, mode="mock")
    out2 = livestock_expert.run(synthetic_livestock_image, mode="mock")
    assert out1 == out2
