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
