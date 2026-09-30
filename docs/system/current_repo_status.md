# Current Repository Status

## 1. Audit Summary
The Unified AI Agri-Vision Platform is currently a functional, integrated prototype. It successfully wires together an offline-first Edge AI pipeline (Zone 1) with Cloud-based Gemini LLM and RAG fallback capabilities (Zone 2) and local SQLite-based farm history persistence (Zone 3). While the architectural foundation and core data contracts are strictly enforced, several advanced AI components (like the semantic domain router) rely on mock/fallback mechanisms for constrained environments or offline demonstrations.

## 2. Repository Snapshot
- **Core App**: Streamlit bilingual UI (Hindi/English).
- **Architecture Zones**: Zone 1 (Edge), Zone 2 (Cloud/RAG), Zone 3 (Memory).
- **Data Contracts**: Explicit JSON contracts enforced across boundaries (defined in `contract.md`).
- **Models**: Integration with Hugging Face transformers (ViT/EfficientNet), and Google Gemini.
- **Tests**: Comprehensive pytest suite across all zones.

## 3. Technology Stack Actually Used
- **Frontend**: Streamlit
- **Edge AI / Vision**: PyTorch, Hugging Face `transformers`, `timm`
- **Cloud / RAG**: `google-genai`, `sentence-transformers`, `faiss-cpu`
- **Database**: SQLite (standard library)

## 4. High-Level Architecture — Actual vs Intended
- **Intended**: Photo/Text/Sensor → MoE routing → Specialist Analysis → Multimodal Fusion → Confidence/Safety Gate → Offline Advisory OR Cloud Escalation → Persistent Private History.
- **Actual**: Implemented accurately, but with practical compromises. Routing uses a zero-shot semantic classifier with a fallback to raw confidence scores. Multimodal Fusion is a deterministic weighted rule-based late fusion.

## 5. Actual Runtime Pipeline
User Input (Image + Optional Text/Sensor)
    ↓
`streamlit_app.py`
    ↓
`pipeline.py` (Quality Check -> Reject if low quality)
    ↓
`task_router.py` (Semantic routing or UI domain selection)
    ↓
`crop_expert.py` OR `livestock_expert.py` (HF Model inference)
    ↓
`fusion.py` (Deterministic weighted adjustment of visual confidence using text/sensor support)
    ↓
`confidence_gate.py` (Decides 'local' vs 'cloud' route based on 80% safety/75% standard threshold + evidence + quality)
    ↓
`local_advisory.py` (If local) OR `gemini_client.py` + `retriever.py` (If cloud)
    ↓
`farm_memory.py` (Saves observation, diagnosis, and advisory)
    ↓
Final Streamlit Output

## 6. Data Flow
Strictly follows `contract.md`:
1. `{"domain", "input_type", "prediction", "confidence", "top_k"}`
2. Farmer Text: `{"text", "language", "confidence"}` (typed description)
3. Text Evidence: `{"symptoms", "crop", "severity_hint"}`
4. Sensor Data: `{"domain", "temperature", "activity", "feed_intake", "anomaly"}`
5. Fusion Output: `{"prediction", "visual_confidence", "text_support", "sensor_support", "evidence_agreement", "final_confidence", "route"}`
6. Cloud Payload: `{"domain", "image_prediction", "visual_confidence", "farmer_text", "text_evidence", "sensor_data", "farm_history", "retrieved_knowledge"}`

## 7. Zone 1 — Edge AI Status
✅ IMPLEMENTED.
The pipeline orchestrates routing, expert inference, multimodal fusion, and confidence gating successfully. Supports a `mock` mode to bypass heavy model loading.

## 8. Zone 2 — Cloud Advisory Status
✅ IMPLEMENTED.
Google Gemini client is functional and expects structured JSON output matching schemas. Enforces strict grounding for citations and farm history acknowledgements via validator. Includes a robust `MockGeminiClient` for offline fallback.

## 9. Zone 3 — Farm Memory Status
✅ IMPLEMENTED.
SQLite database records observations, diagnoses, and advisories. Exposes `get_farm_history` which translates records into recent history strings. Fully integrated into the UI.

## 10. AI/ML Model Status
🟡 PARTIALLY_IMPLEMENTED.
Code references HF checkpoints (`CROP_MODEL_LOCAL_DIR`, `LIVESTOCK_MODEL_LOCAL_DIR`). `crop_expert.py` and `livestock_expert.py` wrap `BaseImageExpert`. Semantic routing relies on a zero-shot classifier. Mock fallbacks are prevalent. 

## 11. RAG Status
✅ IMPLEMENTED.
Uses `faiss-cpu` and `sentence-transformers` for local vector indexing and retrieval. `retriever.py` fetches the top-K relevant documents.

## 12. Multimodal Input Status
✅ IMPLEMENTED.
The farmer's photo, typed symptom description and (for livestock) simulated sensor readings are fused before the confidence gate.

## 13. Offline Capability Status
✅ IMPLEMENTED.
A strong offline-first architecture is present. `MockGeminiClient`, local HF model inference, SQLite memory, and local static advisories all allow the platform to operate entirely without internet access if models are pre-downloaded.

## 14. Confidence & Safety Status
✅ IMPLEMENTED.
`confidence_gate.py` uses dynamic thresholds: 0.80 for safety-critical (e.g., Lumpy Skin Disease, Foot-and-Mouth Disease) and standard thresholds otherwise. Conflicting farmer symptoms or poor input quality enforce cloud escalation.

## 15. UI / Prototype Status
✅ IMPLEMENTED.
Streamlit app is highly polished, bilingual (English/Hindi), featuring distinct flows for Auto-Detect vs Farm History, and integrating authentication, image upload, symptom text, and sensor sliders.

## 16. Database / Farm History Status
✅ IMPLEMENTED.
Standard SQLite implementation. Tables for farm, observations, diagnoses, and advisories are populated automatically during pipeline execution and displayed in the UI's History tab.

## 17. Testing Status
✅ IMPLEMENTED.
A rich pytest suite exists under `tests/` covering Zone 1 (gate, experts, fusion, routing), Zone 2 (gemini, rag), and Zone 3 (auth, memory, stubs).

## 18. Dependencies & Environment
- Requires `pillow`, `pytest`, `numpy`, `huggingface_hub`, `transformers`, `torch`, `streamlit`.
- Cloud features require `google-genai`, `sentence-transformers`, `faiss-cpu`.
- Well-documented `requirements.txt`.

## 19. Mock / Fallback / Placeholder Components
- **Mock Mode**: Prevalent across experts and router to handle constrained hardware.
- **Sensors**: Completely simulated via Streamlit UI sliders.
- **Gemini**: `MockGeminiClient` returns deterministic advisories when `GEMINI_ENABLED=false`.

## 20. Architecture-to-Code Gap Table
| Intended Component | Expected Role | Actual Code Location | Status | Evidence/Notes |
|--------------------|---------------|----------------------|--------|----------------|
| Edge Router | Crop/Livestock routing | `src/zone1_edge/task_router/task_router.py` | ✅ IMPLEMENTED | Correctly handles 3-way routing (Crop, Livestock, None) in real and mock modes without improperly invoking both experts. |
| Crop Expert | Crop disease inference | `src/zone1_edge/experts/crop_expert.py` | ✅ IMPLEMENTED | Wraps `BaseImageExpert`, loads HF models, implements transparent logging of backend inference source. |
| Livestock Expert | Livestock health inference | `src/zone1_edge/experts/livestock_expert.py` | ✅ IMPLEMENTED | Wraps `BaseImageExpert`, loads HF models, implements transparent logging of backend inference source. |
| Quality Check | Input validation | `src/zone1_edge/pipeline/quality_check.py` | ✅ IMPLEMENTED | Handles blur, exposure, resolution, and contrast rejection. |
| Evaluation Tooling | Model baseline testing | `tests/zone1/evaluation_tool.py` | ✅ IMPLEMENTED | Built for offline testing of model baselines with calibration reporting. |
| Multimodal Fusion | Combine evidence | `src/zone1_edge/multimodal/fusion.py` | ✅ IMPLEMENTED | Deterministic weighted late fusion (+/- confidence adjustments). |
| Confidence Gate | Local/cloud decision | `src/zone1_edge/multimodal/confidence_gate.py` | ✅ IMPLEMENTED | Evaluates fusion output, safety criticality, input quality. |
| Cloud Gateway | Escalation | `src/zone2_cloud/gemini/gemini_client.py` | ✅ IMPLEMENTED | Validated schema outputs, integrates Google GenAI. |
| RAG | Knowledge grounding | `src/zone2_cloud/rag/retriever.py` | ✅ IMPLEMENTED | Uses `faiss` and `sentence-transformers`. |
| Farm Memory | Persistent history | `src/zone3_memory/db/farm_memory.py` | ✅ IMPLEMENTED | Uses SQLite, schema logic is active. |

## 21. End-to-End Demo Flows Currently Possible
1. **Flow A (Local Advisory)**: Image Upload -> Routing -> Crop/Livestock Expert -> High Confidence/High Agreement Fusion -> Local Advisory -> Memory Persist.
2. **Flow B (Cloud Escalation)**: Image + Text Upload -> Low Confidence OR Conflicting Symptoms OR Safety Critical -> Cloud Escalation via Gemini + RAG -> Structured Gemini Advisory -> Memory Persist.
3. **Flow C (Mock Mode)**: Hardware constrained offline execution bypassing real model loading for rapid prototyping.

## 22. Known Technical Issues / Risks
- Fusion logic is naive (rule-based score addition/subtraction) rather than an actual trained multi-modal representation.

## 23. Consolidated Future Scope (A-E)
- **Future Scope A**: Multi-Agent Cloud Redesign.
- **Future Scope B**: Secure Aggregation/Federated Learning.
- **Future Scope C**: Real IoT Hardware Integration.
- **Future Scope D**: Admin Dashboard.
- **Future Scope E**: Farm Memory Image Storage (blob storage).
- True multi-modal representation learning (learned fusion).

## 23b. AI Upgrade Status (2026-09-29)
| Item | Status |
|---|---|
| Intra-domain MoE (`moe_gate` + 4 sub-expert slots) | 🟡 Code + training scripts done; inactive until user trains gate/sub-experts (auto-fallback to single expert) |
| Expert fine-tuning (3-stage unfreezing, differential LR) | 🟡 Scripts done; baseline + fine-tune runs pending (user, GPU) |
| Region/season context → local advisory + cloud payload | ✅ Implemented |
| Weather (Open-Meteo, cloud-only) | 🟡 Implemented, disabled by default (`WEATHER_ENABLED`) |
| RAG metadata, doc IDs, lexical fallback, KB gap fill (49 docs) | ✅ Implemented (22 draft docs need expert review) |
| Citation + farm-history hallucination checks | ✅ Implemented |
| LocalLLMClient + backend selector | ✅ Implemented (needs a served fine-tuned model) |
| LLM synthetic data / QLoRA / comparison | 🟡 Scripts done; runs pending (user, Gemini + GPU) |
Details: `docs/system/ai_upgrade_plan.md`.

## 24. Overall Implementation Maturity
High for a prototype. All three roadmap phases (Phase 1: Verification, Phase 2: RAG/Calibration, Phase 3: Cleanup) are complete. The separation of concerns via data contracts between zones is excellently executed and robust.

## 25. Audit Notes / Evidence
- **Pipeline trace**: Fully traced via `src/zone1_edge/pipeline.py::run_zone1_pipeline()`.
- **Fusion rules**: Explicitly hardcoded at `src/zone1_edge/multimodal/fusion.py::_text_agreement()` and bonus additions.
- **RAG & DB**: Local databases act appropriately; RAG index uses FAISS, DB uses SQLite.
