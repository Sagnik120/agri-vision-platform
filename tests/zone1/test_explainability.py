from src.zone1_edge.explainability import explainability

def test_format_top3():
    top_k = [("tomato_early_blight", 0.85), ("healthy", 0.10), ("late_blight", 0.05), ("other", 0.0)]
    res = explainability.format_top3(top_k)
    assert len(res) == 3
    assert res["rank_1"]["label"] == "tomato_early_blight"
    assert res["rank_1"]["confidence"] == 0.85
    assert res["rank_3"]["label"] == "late_blight"

def test_format_top3_short_list():
    top_k = [("healthy", 0.99)]
    res = explainability.format_top3(top_k)
    assert len(res) == 1
    assert res["rank_1"]["label"] == "healthy"

def test_format_reason():
    res = explainability.format_reason(["Confidence below 0.75", "Safety critical"], "cloud")
    assert "cloud tier because: Confidence below 0.75, Safety critical" in res

def test_format_reason_empty():
    res = explainability.format_reason([], "local")
    assert "Routed to local tier." in res
