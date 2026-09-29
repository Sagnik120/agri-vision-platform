"""Intra-domain MoE (moe_gate), label normalisation and region/season context. Offline."""

import json

import numpy as np
import pytest
from PIL import Image

from src.zone1_edge import config
from src.zone1_edge.context.farm_context import build_context, infer_season
from src.zone1_edge.knowledge.label_aliases import normalize_condition
from src.zone1_edge.knowledge.local_advisory import get_advisory
from src.zone1_edge.moe import moe_expert, moe_gate
from src.zone1_edge.moe.expert_groups import CROP_PERENNIAL_CLASSES, CROP_ROW_CLASSES, DOMAIN_GROUPS
from src.zone1_edge.moe.image_features import FEATURE_DIM, extract_features

CONTRACT1 = ["domain", "input_type", "prediction", "confidence", "top_k"]


@pytest.fixture
def img(tmp_path):
    p = tmp_path / "leaf.jpg"
    Image.fromarray(np.random.default_rng(0).integers(0, 255, (80, 80, 3), dtype=np.uint8)).save(p)
    return str(p)


def test_plantvillage_groups_cover_38_disjoint_classes():
    assert len(CROP_ROW_CLASSES) + len(CROP_PERENNIAL_CLASSES) == 38
    assert not set(CROP_ROW_CLASSES) & set(CROP_PERENNIAL_CLASSES)


def test_features_shape(img):
    f = extract_features(img)
    assert f.shape == (FEATURE_DIM,) and np.isfinite(f).all()


def test_learned_gate_from_weights(img):
    groups = list(DOMAIN_GROUPS["crop"])
    w = {"domain": "crop", "groups": groups, "feature_dim": FEATURE_DIM, "mean": [0.0] * FEATURE_DIM,
         "std": [1.0] * FEATURE_DIM, "W": [[0.0] * FEATURE_DIM, [0.0] * FEATURE_DIM], "b": [2.0, 0.0]}
    g = moe_gate.MoEGate("crop", weights=w)
    group, probs = g.select(img)
    assert group == "crop_row" and g.kind == "learned"
    assert abs(sum(probs.values()) - 1) < 1e-3


def test_moe_output_keeps_contract1(img):
    out = moe_expert.MoEDomainExpert("crop", mock=True).predict(img)
    assert list(out)[:5] == CONTRACT1
    assert list(out)[-1] == "_moe" and out["_moe"]["component"] == "moe_gate"
    assert out["prediction"] in DOMAIN_GROUPS["crop"][out["_moe"]["selected_expert"]]


def test_moe_auto_disabled_without_trained_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MOE_DIR", tmp_path)
    monkeypatch.setattr(config, "MOE_ENABLED", "auto")
    assert moe_expert.moe_enabled("crop", "auto") is False
    assert moe_expert.moe_enabled("crop", "mock") is False


def test_label_normalisation_matches_kb():
    assert normalize_condition("Corn___Common_Rust") == "maize_common_rust"
    assert normalize_condition("Corn_(maize)___Common_rust_") == "maize_common_rust"
    assert normalize_condition("Potato___Early_Blight") == "potato_early_blight"
    assert normalize_condition("Pepper,_bell___Bacterial_spot") == "pepper_bacterial_spot"
    assert normalize_condition("Potato___healthy") == "crop_healthy"
    assert normalize_condition("healthy") == "healthy"


def test_season_inference():
    from datetime import date
    assert infer_season(date(2026, 7, 1)) == "kharif"
    assert infer_season(date(2026, 1, 1)) == "rabi"
    assert infer_season(date(2026, 4, 15)) == "zaid"


def test_context_note_does_not_change_diagnosis():
    base = get_advisory("tomato_late_blight")
    ctx = get_advisory("tomato_late_blight", context=build_context("maharashtra", "kharif"))
    assert base["condition"] == ctx["condition"] and base["actions"] == ctx["actions"]
    assert "context_note" not in base
    assert "Monsoon" in ctx["context_note"] and "Maharashtra" in ctx["context_note"]


def test_pipeline_threads_context_and_payload_is_additive(tmp_path):
    from src.zone1_edge.pipeline import build_cloud_payload_stub, run_zone1_pipeline
    p = tmp_path / "crop.jpg"
    Image.fromarray(np.random.default_rng(1).normal(120, 30, (64, 64, 3)).clip(0, 255).astype(np.uint8)).save(p)
    r = run_zone1_pipeline("crop", str(p), mode="mock", region="Punjab", season="rabi")
    if r["gate"]["route"] == "reject":
        pytest.skip("quality check rejected synthetic image")
    assert r["context"] == {"region": "Punjab", "season": "rabi", "season_source": "farmer"}
    payload = build_cloud_payload_stub(r)
    keys = list(payload)
    assert keys[:8] == ["domain", "image_prediction", "visual_confidence", "farmer_text", "text_evidence",
                        "sensor_data", "farm_history", "retrieved_knowledge"]
    assert keys[8:] == ["region", "season", "weather"] and payload["weather"] is None


class _Stub:
    def __init__(self, ans):
        self.ans = ans

    def predict(self, image_path):
        return self.ans


def _both(domain, answers, gate_probs, img):
    m = moe_expert.MoEDomainExpert(domain, mock=True, routing="both")
    m.gate.probs = lambda p: gate_probs
    for g, a in answers.items():
        m._experts[g] = _Stub(a)
    return m.predict(img)


def test_routing_both_crop_takes_most_confident_expert(img):
    out = _both("crop", {"crop_row": [("Tomato___healthy", 0.55), ("x", 0.45)],
                         "crop_perennial": [("Apple___Apple_scab", 0.97), ("y", 0.03)]},
                {"crop_row": 0.9, "crop_perennial": 0.1}, img)  # gate wrong, experts right
    assert out["prediction"] == "Apple___Apple_scab" and out["_moe"]["selected_expert"] == "crop_perennial"
    assert out["_moe"]["gate_choice"] == "crop_row" and out["_moe"]["combine_rule"] == "max_confidence"
    assert list(out)[:5] == CONTRACT1


def test_routing_both_livestock_is_disease_first(img):
    out = _both("livestock", {"livestock_lsd": [("lumpy_skin_disease", 0.60), ("healthy", 0.40)],
                              "livestock_fmd": [("healthy", 0.99), ("foot_and_mouth_disease", 0.01)]},
                {"livestock_lsd": 0.3, "livestock_fmd": 0.7}, img)
    assert out["prediction"] == "lumpy_skin_disease" and out["_moe"]["combine_rule"] == "disease_first"
    healthy = _both("livestock", {"livestock_lsd": [("healthy", 0.9), ("lumpy_skin_disease", 0.1)],
                                  "livestock_fmd": [("healthy", 0.8), ("foot_and_mouth_disease", 0.2)]},
                    {"livestock_lsd": 0.5, "livestock_fmd": 0.5}, img)
    assert healthy["prediction"] == "healthy"


def test_routing_top1_default_and_validation(img):
    out = moe_expert.MoEDomainExpert("crop", mock=True).predict(img)
    assert out["_moe"]["routing"] == "top1" and out["_moe"]["gate_choice"] == out["_moe"]["selected_expert"]
    with pytest.raises(ValueError):
        moe_expert.MoEDomainExpert("crop", mock=True, routing="all")
