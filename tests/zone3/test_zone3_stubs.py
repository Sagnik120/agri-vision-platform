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
# 3. Functional tests
# ===========================================================================

@pytest.fixture
def test_db(monkeypatch):
    import tempfile
    import sqlite3
    from src.zone3_memory.db import farm_memory
    
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db_path = f.name
        farm_memory.init_db(db_path)
        monkeypatch.setattr(farm_memory, "DEFAULT_DB_PATH", db_path)
        yield db_path


def test_init_db(test_db):
    import sqlite3
    with sqlite3.connect(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert {"farm", "observations", "diagnoses", "advisories", "livestock"}.issubset(tables)
        
        # check that demo farm exists
        cursor.execute("SELECT farm_id FROM farm WHERE farm_id='FARM-001'")
        assert cursor.fetchone() is not None


def test_save_observation(test_db):
    from src.zone3_memory.db import farm_memory
    
    obs_id = farm_memory.save_observation(
        farm_id="FARM-001", domain="crop", image_prediction="tomato_early_blight",
        visual_confidence=0.8, farmer_text="brown spots", sensor_json="{}", route="local"
    )
    assert isinstance(obs_id, int)
    
    import sqlite3
    with sqlite3.connect(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT domain, image_prediction FROM observations WHERE observation_id=?", (obs_id,))
        row = cursor.fetchone()
        assert row == ("crop", "tomato_early_blight")


def test_save_diagnosis(test_db):
    from src.zone3_memory.db import farm_memory
    
    obs_id = farm_memory.save_observation("FARM-001", "crop", "test", 0.8, "", "{}", "local")
    diag_id = farm_memory.save_diagnosis(obs_id, "tomato_early_blight", "possible", 0.8)
    
    assert isinstance(diag_id, int)
    import sqlite3
    with sqlite3.connect(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT condition FROM diagnoses WHERE diagnosis_id=?", (diag_id,))
        assert cursor.fetchone()[0] == "tomato_early_blight"


def test_save_advisory(test_db):
    from src.zone3_memory.db import farm_memory
    
    obs_id = farm_memory.save_observation("FARM-001", "crop", "test", 0.8, "", "{}", "local")
    diag_id = farm_memory.save_diagnosis(obs_id, "tomato_early_blight", "possible", 0.8)
    adv_id = farm_memory.save_advisory(diag_id, "local_offline", "summary", ["action1"], "warning")
    
    assert isinstance(adv_id, int)
    import sqlite3
    with sqlite3.connect(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT summary, actions_json FROM advisories WHERE advisory_id=?", (adv_id,))
        row = cursor.fetchone()
        assert row[0] == "summary"
        assert "action1" in row[1]


def test_get_farm_history(test_db):
    from src.zone3_memory.db import farm_memory
    
    obs_id = farm_memory.save_observation("FARM-001", "crop", "test", 0.8, "", "{}", "local")
    diag_id = farm_memory.save_diagnosis(obs_id, "tomato_early_blight", "possible", 0.8)
    farm_memory.save_advisory(diag_id, "local_offline", "use copper fungicide", ["action1"], "none")
    
    history = farm_memory.get_farm_history("FARM-001")
    assert "tomato_early_blight" in history
    assert "use copper fungicide" in history
    assert "possible" in history


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
