"""
sensor_expert.py — Person A, Zone 1 (Hour 3:15-3:45 of the plan).

Simulated livestock sensor panel + threshold rules. NO MODEL — a dict +
if-statements, exactly as the plan specifies. Produces contract.md #4:

    {"domain":"livestock", "temperature": float, "activity": str,
     "feed_intake": str, "anomaly": bool}

Usage:
    python -m src.zone1_edge.multimodal.sensor_expert --temp 40.2 --activity low --feed low
"""

from __future__ import annotations
import argparse
import json
import random

NORMAL_TEMP_RANGE = (38.0, 39.3)
ABNORMAL_TEMP_HIGH = 39.3
ABNORMAL_TEMP_LOW = 37.5
LOW_ACTIVITY_LEVELS = {"low", "very_low"}
LOW_FEED_LEVELS = {"low", "very_low"}

def simulate_reading(anomaly_mode: bool = False, seed: int = None) -> dict:
    """Generate a plausible demo sensor reading."""
    rng = random.Random(seed)
    
    if anomaly_mode:
        # Generate an abnormal reading
        temperature = round(rng.uniform(39.5, 41.5), 1)
        activity = rng.choice(["low", "very_low"])
        feed_intake = rng.choice(["low", "very_low"])
    else:
        # Generate a normal reading
        temperature = round(rng.gauss(38.5, 0.3), 1)
        activity = "normal"
        feed_intake = "normal"
        
    return {
        "temperature": temperature,
        "activity": activity,
        "feed_intake": feed_intake
    }

def compute_trend(current_temp: float, previous_reading: dict | None) -> str:
    if not previous_reading:
        return "stable"
    
    prev_temp = previous_reading.get("temperature", current_temp)
    diff = current_temp - prev_temp
    
    if diff > 0.3:
        return "rising"
    elif diff < -0.3:
        return "falling"
    return "stable"

def top_k_first_aid(sensor_reading: dict, trend: str) -> list[dict]:
    """Return top 3 ranked generic first aid candidates."""
    temp = sensor_reading.get("temperature", 38.5)
    activity = sensor_reading.get("activity", "normal")
    candidates = []
    
    if temp > ABNORMAL_TEMP_HIGH:
        score = 0.6
        if trend == "rising":
            score += 0.2
        if activity in LOW_ACTIVITY_LEVELS:
            score += 0.1
        candidates.append({
            "condition": "Fever/Heat Stress",
            "score": round(score, 2),
            "first_aid": ["Move animal to shade", "Provide plenty of cool water", "Monitor temperature closely"]
        })
        
    if temp < ABNORMAL_TEMP_LOW:
        score = 0.7
        candidates.append({
            "condition": "Hypothermia/Cold Stress",
            "score": round(score, 2),
            "first_aid": ["Provide a dry, draft-free shelter", "Provide additional bedding", "Monitor closely"]
        })
        
    if activity in LOW_ACTIVITY_LEVELS:
        score = 0.5
        candidates.append({
            "condition": "Lethargy/Unknown Infection",
            "score": round(score, 2),
            "first_aid": ["Isolate from herd", "Monitor closely", "Consult local vet if persists"]
        })
        
    if not candidates:
        candidates.append({
            "condition": "Healthy",
            "score": 0.99,
            "first_aid": ["Maintain normal feeding", "Continue regular monitoring"]
        })
        
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:3]

def evaluate(temperature: float, activity: str, feed_intake: str, previous_reading: dict | None = None) -> dict:
    """Apply threshold rules -> contract #4 JSON."""
    anomaly = (
        temperature > ABNORMAL_TEMP_HIGH
        or temperature < ABNORMAL_TEMP_LOW
        or activity in LOW_ACTIVITY_LEVELS
        or feed_intake in LOW_FEED_LEVELS
    )
    
    trend = compute_trend(temperature, previous_reading)
    
    reading_dict = {
        "temperature": temperature,
        "activity": activity,
        "feed_intake": feed_intake
    }
    
    candidates = top_k_first_aid(reading_dict, trend)
    
    return {
        "domain": "livestock",
        "temperature": round(float(temperature), 1),
        "activity": activity,
        "feed_intake": feed_intake,
        "anomaly": bool(anomaly),
        "trend": trend,
        "candidates": candidates
    }

def run(temperature: float = None, activity: str = None, feed_intake: str = None,
        previous_reading: dict | None = None, anomaly_mode: bool = False, seed: int = None) -> dict:
    if temperature is None and activity is None and feed_intake is None:
        reading = simulate_reading(anomaly_mode=anomaly_mode, seed=seed)
        temperature = reading["temperature"]
        activity = reading["activity"]
        feed_intake = reading["feed_intake"]
        
    return evaluate(
        temperature if temperature is not None else 38.5,
        activity or "normal",
        feed_intake or "normal",
        previous_reading=previous_reading
    )

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--temp", type=float, default=None)
    p.add_argument("--activity", type=str, default=None,
                    choices=["normal", "low", "very_low", "high", None])
    p.add_argument("--feed", type=str, default=None,
                    choices=["normal", "low", "very_low", None])
    p.add_argument("--anomaly", action="store_true")
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()
    out = run(args.temp, args.activity, args.feed, anomaly_mode=args.anomaly, seed=args.seed)
    print(json.dumps(out, indent=2))
