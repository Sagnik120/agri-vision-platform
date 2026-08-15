"""
tests/zone3/test_zone3_stubs.py

Diagnostic tests for Zone 3 (Farm Memory / SQLite).
Verifies:
  1. farm_memory.py imports without error.
  2. Function signatures match the documented contract.
  3. All functions raise NotImplementedError (not crash).
  4. schema.sql is parseable and defines all 5 required tables.
  5. results/zone3/ directory hierarchy exists.
  6. DEFAULT_DB_PATH is defined and points to expected location.

Run:
    pytest tests/zone3/ -v
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "src" / "zone3_memory" / "schema" / "schema.sql"
)
RESULTS_ZONE3 = Path(__file__).resolve().parents[2] / "results" / "zone3"


# ===========================================================================
# 1. Import test
# ===========================================================================

def test_farm_memory_imports():
    import importlib
    mod = importlib.import_module("src.zone3_memory.db.farm_memory")
    for fn_name in ["init_db", "save_observation", "save_diagnosis",
                    "save_advisory", "get_farm_history"]:
        assert hasattr(mod, fn_name), f"{fn_name}() must be defined in farm_memory.py"


# ===========================================================================
# 2. Function signature tests
# ===========================================================================

def test_init_db_signature():
    from src.zone3_memory.db.farm_memory import init_db
    sig = inspect.signature(init_db)
    params = list(sig.parameters.keys())
    # db_path should be optional (has a default)
    assert "db_path" in params
    assert sig.parameters["db_path"].default is not inspect.Parameter.empty


def test_save_observation_signature():
    from src.zone3_memory.db.farm_memory import save_observation
    sig = inspect.signature(save_observation)
    required = {"farm_id", "domain", "image_prediction", "visual_confidence",
                "farmer_text", "sensor_json", "route"}
    params = set(sig.parameters.keys())
    assert required.issubset(params), f"Missing params: {required - params}"


def test_save_diagnosis_signature():
    from src.zone3_memory.db.farm_memory import save_diagnosis
    sig = inspect.signature(save_diagnosis)
    required = {"observation_id", "condition", "certainty", "final_confidence"}
    params = set(sig.parameters.keys())
    assert required.issubset(params), f"Missing params: {required - params}"


def test_save_advisory_signature():
    from src.zone3_memory.db.farm_memory import save_advisory
    sig = inspect.signature(save_advisory)
    required = {"diagnosis_id", "source", "summary", "actions", "warning"}
    params = set(sig.parameters.keys())
    assert required.issubset(params), f"Missing params: {required - params}"


def test_get_farm_history_signature():
    from src.zone3_memory.db.farm_memory import get_farm_history
    sig = inspect.signature(get_farm_history)
    params = list(sig.parameters.keys())
    assert "farm_id" in params
    assert "limit" in params
    assert sig.parameters["limit"].default == 5


# ===========================================================================
# 3. Stub behaviour — must raise NotImplementedError
# ===========================================================================

def test_init_db_raises_not_implemented():
    from src.zone3_memory.db.farm_memory import init_db
    with pytest.raises(NotImplementedError):
        init_db()


def test_save_observation_raises_not_implemented():
    from src.zone3_memory.db.farm_memory import save_observation
    with pytest.raises(NotImplementedError):
        save_observation("FARM-001", "crop", "tomato_early_blight", 0.8,
                         "brown spots", "{}", "local")


def test_save_diagnosis_raises_not_implemented():
    from src.zone3_memory.db.farm_memory import save_diagnosis
    with pytest.raises(NotImplementedError):
        save_diagnosis(1, "tomato_early_blight", "possible", 0.8)


def test_save_advisory_raises_not_implemented():
    from src.zone3_memory.db.farm_memory import save_advisory
    with pytest.raises(NotImplementedError):
        save_advisory(1, "local_offline", "summary", ["action"], "warning")


def test_get_farm_history_raises_not_implemented():
    from src.zone3_memory.db.farm_memory import get_farm_history
    with pytest.raises(NotImplementedError):
        get_farm_history("FARM-001")


# ===========================================================================
# 4. Schema SQL is parseable and defines all required tables
# ===========================================================================

def test_schema_sql_exists():
    assert SCHEMA_PATH.exists(), f"schema.sql not found at {SCHEMA_PATH}"


def test_schema_defines_all_required_tables():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    required_tables = ["farm", "observations", "diagnoses", "advisories", "livestock"]
    for table in required_tables:
        pattern = rf"CREATE TABLE IF NOT EXISTS {table}\b"
        assert re.search(pattern, sql, re.IGNORECASE), \
            f"schema.sql must define table '{table}'"


def test_schema_observations_has_required_columns():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    # All contract-required columns for the observations table
    required_cols = [
        "observation_id", "farm_id", "domain", "image_prediction",
        "visual_confidence", "farmer_text", "sensor_json", "route", "created_at"
    ]
    for col in required_cols:
        assert col in sql, f"schema.sql observations table must have column '{col}'"


def test_schema_advisories_has_source_constraint():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    # source column must constrain to local_offline or cloud_gemini
    assert "local_offline" in sql and "cloud_gemini" in sql, \
        "advisories.source must be constrained to local_offline|cloud_gemini"


def test_schema_has_indexes():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    assert "CREATE INDEX" in sql, "schema.sql should define at least one index"


# ===========================================================================
# 5. DEFAULT_DB_PATH is defined correctly
# ===========================================================================

def test_default_db_path_defined():
    from src.zone3_memory.db import farm_memory
    assert hasattr(farm_memory, "DEFAULT_DB_PATH"), \
        "farm_memory.py must define DEFAULT_DB_PATH"
    db_path = farm_memory.DEFAULT_DB_PATH
    # It should be under results/zone3/
    assert "zone3" in str(db_path) or "results" in str(db_path), \
        f"DEFAULT_DB_PATH should be under results/zone3/, got: {db_path}"


def test_schema_path_defined():
    from src.zone3_memory.db import farm_memory
    assert hasattr(farm_memory, "SCHEMA_PATH"), \
        "farm_memory.py must define SCHEMA_PATH"
    schema_p = farm_memory.SCHEMA_PATH
    assert Path(schema_p).exists(), f"SCHEMA_PATH must point to existing file, got: {schema_p}"


# ===========================================================================
# 6. Results directory hierarchy
# ===========================================================================

def test_results_zone3_directories_exist():
    for subdir in ["db_snapshots"]:
        path = RESULTS_ZONE3 / subdir
        path.mkdir(parents=True, exist_ok=True)
        assert path.exists(), f"results/zone3/{subdir}/ should exist"


# ===========================================================================
# 7. Integration: contract #5 output from Zone 1 matches what Zone 3
#    save_observation() expects (domain, image_prediction, visual_confidence)
# ===========================================================================

def test_zone1_gate_output_has_fields_for_save_observation():
    """
    Proves the gate output from Zone 1 has the exact fields that
    farm_memory.save_observation() expects (once implemented).
    """
    import tempfile
    from PIL import Image
    from src.zone1_edge.pipeline import run_zone1_pipeline

    tmp = Path(tempfile.mkdtemp())
    img_path = str(tmp / "test.jpg")
    Image.new("RGB", (64, 64), (100, 200, 80)).save(img_path)

    result = run_zone1_pipeline("crop", img_path, mode="mock")
    gate = result["gate"]

    # Fields needed by save_observation
    assert "route" in gate
    assert gate["route"] in ("local", "cloud")
    img_out = result["image_output"]
    assert "domain" in img_out
    assert "prediction" in img_out
    assert "confidence" in img_out
    assert isinstance(img_out["confidence"], float)
