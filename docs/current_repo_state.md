# Agri-Vision Platform - Current Repository State

## 1. Overview
The **Agri-Vision Platform** is an AI-powered agricultural diagnostic and advisory system. It is designed to assist farmers by analyzing crop and livestock images, sensor data, and textual symptoms to provide localized, actionable advisories. The platform is structured around a multi-zone architecture, prioritizing edge computing for offline resilience while leveraging cloud capabilities for complex queries.

This document outlines the current state of the repository's codebase, detailing the purpose, implementation, and rationale behind each core component.

---

## 2. System Architecture & Components

The architecture is divided into three primary zones: **Zone 1 (Edge Computing)**, **Zone 2 (Cloud AI)**, and **Zone 3 (Memory & State)**.

### 2.1 Zone 1: Edge Computing (`src/zone1_edge/`)
- **Why used**: Ensures the platform remains functional in low-connectivity rural environments by executing core diagnostics locally.
- **How implemented**:
  - **Pipeline (`pipeline.py`)**: The central entrypoint for local execution. It orchestrates routing, quality checks, and expert inferences.
  - **Task Router (`task_router/task_router.py`)**: Dynamically routes inputs to either the crop or livestock pipelines based on input features or heuristics.
  - **Quality Check (`quality/quality_check.py`)**: Validates image integrity (blur, exposure) using OpenCV before processing, ensuring garbage inputs do not produce garbage outputs.
  - **Experts (`experts/crop_expert.py`, `experts/livestock_expert.py`, `multimodal/sensor_expert.py`)**: Local heuristic and ML-lite models that analyze visual embeddings and sensor anomalies (e.g., detecting fever from temperature arrays).
  - **Text Evidence (`multimodal/text_evidence.py`)**: Extracts structured symptoms from natural language (including regional languages like Hindi) using local NLP techniques.
  - **Fusion (`multimodal/fusion.py`)**: Aggregates multi-modal signals (image confidence, text symptoms, sensor readings) to compute a `final_confidence` score.
  - **Gate (`multimodal/confidence_gate.py`)**: Decides whether the local confidence is sufficient or if the query must be routed to the Cloud (Zone 2) for advanced analysis.

### 2.2 Zone 2: Cloud AI & RAG (`src/zone2_cloud/`)
- **Why used**: Handles complex, ambiguous, or low-confidence edge cases by leveraging advanced Large Language Models and comprehensive knowledge bases.
- **How implemented**:
  - **Gemini Client (`gemini/gemini_client.py`)**: Integrates with Google's Gemini models for deep, reasoning-based diagnostics when local heuristics fall short. It also natively handles **PII Stripping** (redacting Personally Identifiable Information) before transmitting local data to the cloud to ensure privacy compliance.
  - **Retrieval-Augmented Generation (`rag/`)**: 
    - Uses `sentence-transformers` and vector databases (via `build_knowledge_base.py` and `retriever.py`) to retrieve localized agricultural best practices and disease treatments.
    - Grounds the LLM's responses in factual, regional agricultural knowledge to prevent hallucination.
  - **Validator (`gemini/validator.py`)**: Post-processes cloud outputs to ensure safety, stripping out ungrounded advice or dangerous chemical recommendations.

### 2.3 Zone 3: Memory & State (`src/zone3_memory/`)
- **Why used**: Maintains persistent state, farmer profiles, and historical diagnostic records to track farm health over time.
- **How implemented**:
  - **Database (`db/farm_memory.py`)**: Uses **SQLite** for lightweight, persistent relational storage of farms, observations, diagnoses, and advisories.
  - **Authentication (`db/auth.py`)**: Manages secure farmer registration and session handling, isolating data via distinct `farm_id`s.

### 2.4 Application Interface (`src/app/`)
- **Why used**: Provides an accessible, interactive User Interface for farmers and extension workers to input data and receive advisories.
- **How implemented**:
  - Built using **Streamlit** (`streamlit_app.py`) for rapid, data-centric UI development.
  - Currently supports Image upload, Text input, and Sensor data input.
  - *Note*: Voice (ASR/TTS) functionality has been temporarily disabled behind a `VOICE_INPUT_ENABLED` feature flag as part of the Phase 3 stabilization.

### 2.5 Testing Suite (`tests/`)
- **Why used**: Ensures pipeline reliability, contract adherence between zones, and prevents regressions during active development.
- **How implemented**:
  - Extensive **Pytest** suite covering Unit, Integration, and End-to-End (E2E) flows.
  - Specific workarounds (e.g., Pytest skips) are implemented to safely bypass known Windows C-extension loading conflicts with OpenCV (`cv2`) and NumPy.
  - Database tests use isolated `tmp_path` fixtures to prevent state pollution and file locking issues.

---

## 3. Data Flow & Execution Contracts

1. **Input**: The Streamlit UI collects multi-modal inputs (Image + Text + Sensors).
2. **Local Processing (Zone 1)**: The `run_zone1_pipeline` processes inputs locally. It attempts to generate a `local_advisory`. 
3. **Routing Decision**: The `gate` outputs a route (`local` or `cloud`).
4. **Cloud Processing (Zone 2)**: If routed to `cloud`, the UI triggers the RAG retrieval and Gemini API using the standardized `cloud_payload` generated by Zone 1.
5. **Persistence (Zone 3)**: Both local and cloud outcomes are saved to the SQLite database via `farm_memory.save_observation()`, building a longitudinal health record.
