# Zone 1 Edge Details

## 1. Purpose
Provides the offline-first edge AI reasoning.

## Key Responsibilities
- **Quality Gate:** Checks image blur (Laplacian variance), exposure, resolution (>= 50px), and contrast. Rejects invalid images immediately.
- **Task Router:** Identifies whether the input is a crop, livestock, or "none" (irrelevant image). If "none", it short-circuits the pipeline before invoking any expert.
- **Multimodal Experts:** Dedicated submodules for image, text, and sensor data.
  - Image experts embed transparent tracking (real vs. mock backend).
- **Fusion:** Deterministic weighted fusion using `WEIGHT_VISUAL` (0.6), `WEIGHT_TEXT_SUPPORT` (0.2), and `WEIGHT_SENSOR_SUPPORT` (0.2) to calculate the final confidence score. Confidence is strictly bounded [0.01, 0.99] unless maxed.

## 3. Architecture Role
The primary inference engine. Determines if cloud escalation is necessary.

## 4. Inputs
Image paths, simulated sensor dictionaries, transcribed Hindi text.

## 5. Outputs
Returns the finalized Contract 5 (Fusion Output + Gate Routing Decision).

## 6. Important files
- `pipeline.py`: Orchestrator.
- `fusion.py`: Rule-based combination.
- `confidence_gate.py`: Gateway threshold checks.

## 7. Dependencies
`torch`, `transformers`, `huggingface_hub`.

## 8. Runtime flow
Called by `streamlit_app.py`. Dispatches to router, then experts, then fusion, then gate.

## 9. Contracts/interfaces
Produces Contracts 1, 3, 4. Outputs Contract 5.

## 10. Current implementation status
IMPLEMENTED (with mock fallbacks heavily utilized).

## 11. Important assumptions
Assumes local models are downloaded in `setup/`.

## 12. Known limitations
Fusion is rule-based, not a learned vector embedding space.
