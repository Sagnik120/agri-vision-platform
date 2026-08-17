from src.zone1_edge.multimodal import sensor_expert


def test_normal_reading_no_anomaly():
    out = sensor_expert.run(temperature=38.5, activity="normal", feed_intake="normal")
    assert out["anomaly"] is False
    assert set(out.keys()) == {"domain", "temperature", "activity", "feed_intake", "anomaly", "trend", "candidates"}
    assert out["domain"] == "livestock"
    assert out["trend"] == "stable"
    assert out["candidates"][0]["condition"] == "Healthy"


def test_high_temp_triggers_anomaly_and_trend():
    out = sensor_expert.run(temperature=40.5, activity="normal", feed_intake="normal", previous_reading={"temperature": 39.0})
    assert out["anomaly"] is True
    assert out["trend"] == "rising"
    assert out["candidates"][0]["condition"] == "Fever/Heat Stress"


def test_low_activity_triggers_anomaly():
    out = sensor_expert.run(temperature=38.5, activity="low", feed_intake="normal")
    assert out["anomaly"] is True
    assert out["candidates"][0]["condition"] == "Lethargy/Unknown Infection"


def test_low_feed_triggers_anomaly():
    out = sensor_expert.run(temperature=38.5, activity="normal", feed_intake="very_low")
    assert out["anomaly"] is True


def test_simulated_reading_runs_without_error():
    out = sensor_expert.run(seed=1)
    assert isinstance(out["anomaly"], bool)
    assert "trend" in out
    assert "candidates" in out
