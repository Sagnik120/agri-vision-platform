from src.zone1_edge.knowledge import local_advisory


def test_known_condition_lookup():
    out = local_advisory.get_advisory("tomato_early_blight")
    assert out["condition"] == "tomato_early_blight"
    assert out["source"] == "local_offline"
    assert isinstance(out["actions"], list) and len(out["actions"]) > 0
    assert isinstance(out["summary"], str) and out["summary"]


def test_all_10_plus_entries_present():
    import json
    from src.zone1_edge import config
    with open(config.KNOWLEDGE_DIR / "local_advisories.json") as f:
        db = json.load(f)
    assert len(db) >= 10


def test_unknown_condition_falls_back_gracefully():
    out = local_advisory.get_advisory("some_never_seen_condition_xyz")
    assert out["condition"] == "some_never_seen_condition_xyz"
    assert "actions" in out and len(out["actions"]) > 0
