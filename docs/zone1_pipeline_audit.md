# Zone 1 Pipeline Audit (Person A)

## 1. Capture & Quality Check
- **Behavior**: Uses OpenCV to compute a Laplacian variance blur score and a pixel-luminance exposure score. If the normalized score is below a threshold, it rejects or warns.
- **Model**: None (pure deterministic computer vision rules).
- **Status**: `MATCHES PLAN`

## 2. Task Router
- **Behavior**: Provides explicit `crop` or `livestock` routing, but also implements an `auto_route` function that uses a zero-shot vision model to guess the domain.
- **Model**: `openai/clip-vit-base-patch32`
- **Status**: `DEVIATES FROM PLAN (describe how)` - The plan explicitly specified this should be UI-driven (user clicks Crop or Livestock). The code has introduced a learned classifier for auto-routing, which adds an undocumented point of failure and latency.

## 3. Crop Expert
- **Behavior**: Loads a pretrained image classifier to identify crop diseases, applying basic torchvision transforms (Resize, CenterCrop, Normalize). Outputs a contract-compliant dict.
- **Model**: `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` (Fallback: `wambugu71/crop_leaf_diseases_vit`).
- **Status**: `MATCHES PLAN`

## 4. Livestock Expert
- **Behavior**: Extracts image features and attempts to classify livestock conditions.
- **Model**: `openai/clip-vit-base-patch32`
- **Status**: `MATCHES PLAN` - However, it relies heavily on zero-shot CLIP rather than a specialized livestock checkpoint, which is a known limitation in the plan.

## 5. Sensor Expert
- **Behavior**: Takes temperature, activity, and feed intake, comparing them against hardcoded biological norms for cattle (e.g., Temp > 39.5 = fever).
- **Model**: None (deterministic rules).
- **Status**: `MATCHES PLAN`

## 6. Text-Evidence Extractor
- **Behavior**: Uses a hardcoded mapping dictionary to scan raw ASR transcripts for specific Hindi and English symptom keywords.
- **Model**: None (deterministic string matching).
- **Status**: `MATCHES PLAN` - Keywords like "भूरे धब्बे" and "पीली पत्तियां" are correctly mapped.

## 7. Fusion Module
- **Behavior**: Implements the arithmetic rule: base visual score, +0.10 for text support, -0.20 for text conflict. +0.08 for sensor support, -0.15 for sensor conflict. Caps at 0.99, floors at 0.01.
- **Model**: None.
- **Status**: `MATCHES PLAN` - Arithmetic exactly matches the spec.

## 8. Confidence & Safety Gate
- **Behavior**: Evaluates fusion output against `config.GATE_CONFIDENCE_THRESHOLD`.
- **Status**: `BROKEN` - The logic in `is_high_confidence` is missing the `not is_critical` check. This means safety-critical diseases with high visual confidence are erroneously routed to `local` instead of `cloud`. Additionally, the dynamic threshold formula by device tier is currently stubbed/hardcoded.

## 9. Local Advisory
- **Behavior**: JSON file containing localized advisory text and action steps for common predictions.
- **Status**: `MATCHES PLAN`

## 10. Streamlit Integration (Person A's side)
- **Behavior**: Implements a unified flow passing data to `run_zone1_pipeline`.
- **Status**: `MATCHES PLAN` - The UI successfully handles both domains through a unified `Auto-Detect` interface.

---

## Adversarial Test Log

```text
=================================== FAILURES ===================================
______________________ test_safety_critical_routes_cloud _______________________
AssertionError: assert 'local' == 'cloud'
tests/zone1/test_confidence_gate.py:45: AssertionError

____________________________ test_dynamic_threshold ____________________________
AssertionError: assert 'local' == 'cloud'
tests/zone1/test_confidence_gate.py:53: AssertionError

_________________________ test_device_tier_resilience __________________________
assert None is False
tests/zone1/test_fusion.py:99: AssertionError
```

## Cloud Escalation Contract Verification (Person A's Outbound Side)
- **Model**: Hardcoded as Gemini for cloud escalation.
- **Tradeoff Justification**: Gemini provides the necessary reasoning depth to evaluate multi-modal evidence safely, avoiding hallucinated veterinary advice.
- **System Prompt**: Enforces safety constraints correctly.
- **Payload**: Complies perfectly with the Section 2 JSON data contract.
