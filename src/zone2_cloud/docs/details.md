# Zone 2 Cloud Details

## 1. Purpose
Provides expert-level agronomic escalation using Gemini and local RAG.

## 2. Responsibilities
- Retrieves context from a FAISS vector index.
- Packages images, text, sensors, and history into a prompt.
- Validates the JSON schema returned by Gemini, enforcing cited knowledge grounding and farm history acknowledgement.

## 3. Architecture Role
The escalation layer (triggered when Zone 1 lacks confidence).

## 4. Inputs
Contract 6 (Cloud Request Payload).

## 5. Outputs
Valid JSON schema dict containing diagnosis and advisory.

## 6. Important files
- `gemini_client.py`: API integration and fallback mock.
- `retriever.py`: RAG logic.

## 7. Dependencies
`google-genai`, `faiss-cpu`, `sentence-transformers`.

## 8. Runtime flow
Called by `streamlit_app.py` when `route == 'cloud'`.

## 9. Contracts/interfaces
Consumes Contract 6.

## 10. Current implementation status
IMPLEMENTED.

## 11. Important assumptions
Assumes `results/zone2/rag_index` exists. Assumes valid Gemini API key if `GEMINI_ENABLED=true`.

## 12. Known limitations
RAG is currently restricted to small local Markdown files.
