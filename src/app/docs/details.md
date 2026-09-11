# Streamlit App Details

## 1. Purpose
Provides the primary farmer-facing, bilingual interface (English/Hindi).

## 2. Responsibilities
- User authentication.
- File (Image/Voice) uploading.
- Sensor data simulation (via sliders).
- Wires the execution of Zone 1 (`pipeline.py`).
- Handles UI branching based on the final decision (`local` vs `cloud`).

## 3. Architecture Role
The presentation layer spanning all three zones.

## 4. Inputs
User interactions, files, login credentials.

## 5. Outputs
Visual Streamlit components, advisories, historical tables.

## 6. Important files
- `streamlit_app.py`: The single entry point.

## 7. Dependencies
`streamlit`, `zone1_edge.pipeline`, `zone2_cloud.gemini`, `zone3_memory.db`.

## 8. Runtime flow
Called via `streamlit run src/app/streamlit_app.py`. Initializes DB, checks login, and awaits User interactions before calling pipeline.

## 9. Contracts/interfaces
Consumes Contract 5 (Fusion output) to determine the next view state.

## 10. Current implementation status
IMPLEMENTED.

## 11. Important assumptions
Assumes local DB is accessible. Assumes offline fallback models are cached.

## 12. Known limitations
Voice processing via Streamlit upload is a simulation of native app microphone input.
