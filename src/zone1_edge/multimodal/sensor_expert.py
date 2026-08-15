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

# Normal ranges for cattle (demo thresholds, not veterinary advice)
NORMAL_TEMP_RANGE = (38.0, 39.3)          # Celsius
ABNORMAL_TEMP_HIGH = 39.3
ABNORMAL_TEMP_LOW = 37.5
LOW_ACTIVITY_LEVELS = {"low", "very_low"}
LOW_FEED_LEVELS = {"low", "very_low"}


def simulate_reading(seed: int = None) -> dict:
    """Generate a plausible demo sensor reading (for when no real sensor exists)."""
    rng = random.Random(seed)
    temperature = round(rng.uniform(37.0, 40.5), 1)
    activity = rng.choice(["normal", "low", "very_low", "high"])
    feed_intake = rng.choice(["normal", "low", "very_low"])
    return evaluate(temperature, activity, feed_intake)


def evaluate(temperature: float, activity: str, feed_intake: str) -> dict:
    """Apply threshold rules -> contract #4 JSON."""
    anomaly = (
        temperature > ABNORMAL_TEMP_HIGH
        or temperature < ABNORMAL_TEMP_LOW
        or activity in LOW_ACTIVITY_LEVELS
        or feed_intake in LOW_FEED_LEVELS
    )
    return {
        "domain": "livestock",
        "temperature": round(float(temperature), 1),
        "activity": activity,
        "feed_intake": feed_intake,
        "anomaly": bool(anomaly),
    }


def run(temperature: float = None, activity: str = None, feed_intake: str = None,
        seed: int = None) -> dict:
    if temperature is None and activity is None and feed_intake is None:
        return simulate_reading(seed=seed)
    return evaluate(
        temperature if temperature is not None else 38.5,
        activity or "normal",
        feed_intake or "normal",
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--temp", type=float, default=None)
    p.add_argument("--activity", type=str, default=None,
                    choices=["normal", "low", "very_low", "high", None])
    p.add_argument("--feed", type=str, default=None,
                    choices=["normal", "low", "very_low", None])
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()
    out = run(args.temp, args.activity, args.feed, seed=args.seed)
    print(json.dumps(out, indent=2))
