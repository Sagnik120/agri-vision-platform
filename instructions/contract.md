# Shared Data Contract — Agri-Vision Platform

Frozen at Minute 0–15. **Do not change a shape without telling the other person.**
All modules MUST return exactly these keys/types. Extra keys are allowed to be
added at the END for debugging (e.g. `_debug`), but never remove/rename the
keys below.

## 1. Image expert output (Person A → crop_expert.py / livestock_expert.py)
```json
{"domain": "crop|livestock", "input_type": "image", "prediction": "str", "confidence": 0.0, "top_k": [["label", 0.0]]}
```

## 2. ASR output (Person B → zone2_cloud/asr)
```json
{"text": "str", "language": "hi", "confidence": null}
```

## 3. Text evidence output (Person A, consumes Person B's ASR text)
```json
{"symptoms": ["str"], "crop": "str", "severity_hint": "str"}
```

## 4. Sensor output (Person A, simulated)
```json
{"domain": "livestock", "temperature": 0.0, "activity": "str", "feed_intake": "str", "anomaly": false}
```

## 5. Fusion output (Person A → consumed by Person B's cloud call + UI)
```json
{"prediction": "str", "visual_confidence": 0.0, "text_support": false, "sensor_support": null, "evidence_agreement": "high|medium|low", "final_confidence": 0.0, "route": "local|cloud"}
```

## 6. Cloud request payload (Person B builds this FROM Person A's fusion output)
```json
{"domain": "str", "image_prediction": "str", "visual_confidence": 0.0, "farmer_text": "str", "text_evidence": ["str"], "sensor_data": null, "farm_history": "str", "retrieved_knowledge": "str"}
```

## Ownership
| Contract shape | Producer | Consumer |
|---|---|---|
| Image expert output | Person A | Fusion (Person A), UI |
| ASR output | Person B | Text evidence (Person A) |
| Text evidence output | Person A | Fusion (Person A) |
| Sensor output | Person A | Fusion (Person A) |
| Fusion output | Person A | Confidence gate (Person A), Cloud payload builder (Person B), UI |
| Cloud request payload | Person B | Gemini client (Person B) |

## Integration checkpoints
- **0:00–0:15** — Contract freeze (this file)
- **2:00–2:30** — Checkpoint 1: Person A experts + Person B ASR both emit valid contract JSON
- **6:15–6:45** — Checkpoint 2: Person A fusion+gate output correctly drives Person B's local-vs-cloud branch
- **7:30–8:00** — Final end-to-end test
