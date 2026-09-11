# Zone 3 Memory Details

## 1. Purpose
Provides persistent local storage for the farm's history.

## 2. Responsibilities
- Local Authentication.
- Saving observations, diagnoses, and advisories.
- Generating farm history strings.

## 3. Architecture Role
The data persistence layer. Feeds historical context back into Zone 2.

## 4. Inputs
Final inference details and farmer UI events.

## 5. Outputs
Formatted strings for RAG context and DataFrames for Streamlit UI.

## 6. Important files
- `farm_memory.py`: SQLite DB operations.
- `schema.sql`: Table layouts.

## 7. Dependencies
`sqlite3` (built-in).

## 8. Runtime flow
Called directly by `streamlit_app.py` post-inference.

## 9. Contracts/interfaces
Implicit mappings to Contract 6 (`farm_history` string).

## 10. Current implementation status
IMPLEMENTED.

## 11. Important assumptions
DB is lightweight and suitable for local device storage.

## 12. Known limitations
Not currently synced to a central cloud dashboard.
