# Agri-Vision 3-Zone Architecture

The system is separated into three highly decoupled zones communicating via strict JSON contracts.

## Zone 1: Edge AI
- **Orchestrator:** `src/zone1_edge/pipeline.py`
- **Responsibilities:** Evaluates images and simulated sensor data. Fuses symptoms mathematically to adjust visual confidence. Gates decisions into `local` or `cloud` routes.
- **Models:** EfficientNet/MobileNet via Hugging Face.

## Zone 2: Cloud Advisory
- **Orchestrator:** `src/zone2_cloud/gemini/gemini_client.py`
- **Responsibilities:** Receives escalated cases. Queries local FAISS RAG index. Prompts Gemini for an expert advisory payload. 

## Zone 3: Farm Memory
- **Orchestrator:** `src/zone3_memory/db/farm_memory.py`
- **Responsibilities:** Manages SQLite database logging observations and diagnoses. Generates historical strings to feed into Zone 2's cloud context.
