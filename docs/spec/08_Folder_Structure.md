# Agri-Vision Platform - Detailed Folder Structure

This document provides a comprehensive overview of the repository's folder structure, highlighting the purpose and responsibilities of each directory and significant file.

## 📂 Root Directory
The root directory contains high-level project configuration.
*   `README.md`: The main project documentation explaining the problem statement, solution, architecture, and setup instructions.
*   `requirements.txt`: The Python dependencies needed to run the project.
*   `architecture_diagram.png`: Visual representation of the 3-Zone system architecture.

---

## 📂 `docs/` (Documentation)
Contains all specifications and audit logs.
*   **`spec/`**: Core project specifications (PRD, Architecture, Rules, Folder Structure, Testing, Git Discipline, Token Efficiency).
*   **`system/`**: Audit results and system state files (`current_repo_status.md`, `code_files.md`).

---

## 📂 `instructions/` (Protected Contracts)
Contains frozen data contracts.
*   `contract.md`: The formal JSON specification passed between the Edge, Cloud, and Memory zones. Do not alter.

---

## 📂 `src/` (Source Code)
The core of the application, strictly organized into the 3-Zone architecture.

### 📁 `src/app/`
Contains the main farmer-facing user interface.
*   `streamlit_app.py`: The bilingual (Hindi/English) Streamlit application.
*   `docs/details.md`: Component responsibilities.

### 📁 `src/zone1_edge/` (Zone 1 - Edge AI)
Handles offline-first, on-device operations.
*   `pipeline.py`: The orchestrator for Zone 1.
*   `config.py`: Global configuration.
*   **`experts/`**, **`multimodal/`**, **`task_router/`**, **`knowledge/`**, **`speech/`**, **`demo_data/`**: Submodules.
*   `docs/details.md`: Component responsibilities.

### 📁 `src/zone2_cloud/` (Zone 2 - Cloud Advisory)
Triggered when Zone 1 escalates an issue.
*   **`gemini/`**: API Client.
*   **`rag/`**: Vector retrieval logic.
*   `docs/details.md`: Component responsibilities.

### 📁 `src/zone3_memory/` (Zone 3 - Farm Memory)
Manages persistent historical records.
*   **`db/`**: SQLite database operations.
*   **`schema/`**: Database tables setup.
*   `docs/details.md`: Component responsibilities.

---

## 📂 `setup/` (Environment & Setup)
Contains scripts necessary to bootstrap the environment and download ML models.
*   `setup_venv.sh`, `download_crop_model.py`, `download_livestock_model.py`, `diagnose_pipeline.py`.

---

## 📂 `tests/` (Testing Suite)
Contains the test suite verifying the integrity of the platform, structured to mirror `src/`.
*   **`zone1/`**, **`zone2/`**, **`zone3/`**, **`app/`**.

---

## 📂 `results/` (Generated Artifacts)
Stores outputs generated during runtime, setup, or evaluation.
*   **`zone1/`**: Logs from diagnostic runs.
*   **`zone2/rag_index/`**: FAISS indexes.
*   **`zone3/`**: SQLite database.
