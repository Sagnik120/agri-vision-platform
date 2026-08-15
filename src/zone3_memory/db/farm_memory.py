"""
farm_memory.py — STUB. Person B, Zone 3 (Hour 3:30-4:15 of the plan).

GOAL: SQLite-backed Private Farm Memory. Tables defined in
../schema/schema.sql (farm, observations, diagnoses, advisories, livestock).

EXPECTED FUNCTIONS (signatures fixed — fill in bodies):

    def init_db(db_path: str = "farm_memory.db") -> None:
        '''Create tables from schema.sql if they don't exist.'''

    def save_observation(farm_id: str, domain: str, image_prediction: str,
                          visual_confidence: float, farmer_text: str,
                          sensor_json: str, route: str,
                          animal_id: str = None) -> int:
        '''Insert a row into observations, return the new observation_id.
        Call this every time run_zone1_pipeline() completes, regardless of
        route local/cloud.'''

    def save_diagnosis(observation_id: int, condition: str, certainty: str,
                        final_confidence: float) -> int:
        '''Insert into diagnoses, return diagnosis_id.'''

    def save_advisory(diagnosis_id: int, source: str, summary: str,
                       actions: list, warning: str) -> int:
        '''Insert into advisories (actions serialized as JSON), return advisory_id.'''

    def get_farm_history(farm_id: str, limit: int = 5) -> str:
        '''Return prior diagnoses for this farm as a human-readable string,
        most recent first — this becomes contract.md #6's `farm_history`
        field for the Gemini cloud call. E.g.:
        "5 days ago: tomato_early_blight (possible), advised copper fungicide.
         12 days ago: healthy check, no issues found."'''

TODO:
  1. `import sqlite3` (stdlib, no install needed).
  2. Implement init_db() by reading and executing ../schema/schema.sql.
  3. Implement the CRUD functions above.
  4. Wire save_observation/save_diagnosis/save_advisory to be called after
     EVERY analysis run (both local and cloud routes) — this is what proves
     "Private Farm Memory" in the final demo (Section 8, 4th bullet:
     "Re-run a similar case -> system says 'a similar issue was recorded on
     this farm N days ago'").

Suggested agent prompt:
    "Implement init_db, save_observation, save_diagnosis, save_advisory, and
    get_farm_history using Python's sqlite3 stdlib module, following the
    schema in ../schema/schema.sql exactly. get_farm_history should return a
    readable string summarizing the farm's last N diagnoses with how many
    days ago each occurred."
"""

from __future__ import annotations

from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "schema.sql"
DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "results" / "zone3" / "farm_memory.db"


def init_db(db_path: str = None) -> None:
    raise NotImplementedError("TODO: create tables from schema.sql. See docstring.")


def save_observation(farm_id: str, domain: str, image_prediction: str,
                      visual_confidence: float, farmer_text: str,
                      sensor_json: str, route: str, animal_id: str = None) -> int:
    raise NotImplementedError("TODO: insert into observations table.")


def save_diagnosis(observation_id: int, condition: str, certainty: str,
                    final_confidence: float) -> int:
    raise NotImplementedError("TODO: insert into diagnoses table.")


def save_advisory(diagnosis_id: int, source: str, summary: str,
                   actions: list, warning: str) -> int:
    raise NotImplementedError("TODO: insert into advisories table.")


def get_farm_history(farm_id: str, limit: int = 5) -> str:
    raise NotImplementedError("TODO: query + format prior diagnoses. See docstring.")


if __name__ == "__main__":
    init_db()
    print(f"DB initialized at {DEFAULT_DB_PATH}")
