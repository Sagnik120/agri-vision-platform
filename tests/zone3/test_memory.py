import pytest
from src.zone3_memory.db import farm_memory
from src.zone3_memory.db.auth import signup
import os
from pathlib import Path
from src.zone2_cloud.gemini.gemini_client import strip_pii

# Override DB path for tests
test_db = Path("test_memory.db")
farm_memory.DEFAULT_DB_PATH = test_db

def setup_module():
    if test_db.exists():
        test_db.unlink()
    farm_memory.init_db()

def teardown_module():
    if test_db.exists():
        test_db.unlink()

def test_scoped_memory():
    # Create two farmers
    f1 = signup("111", "0000", "Farmer 1")
    f2 = signup("222", "0000", "Farmer 2")
    
    # Save observation for f1
    obs_id = farm_memory.save_observation(f1, "crop", "healthy", 0.9, "Looks ok", "{}", "local")
    diag_id = farm_memory.save_diagnosis(obs_id, "healthy", "confirmed", 0.95)
    farm_memory.save_advisory(diag_id, "local_offline", "All good", ["None"], "None")
    
    # Get history for f1
    h1 = farm_memory.get_farm_history(f1)
    assert "healthy" in h1
    
    # Get history for f2 (should be empty)
    h2 = farm_memory.get_farm_history(f2)
    assert "No prior history" in h2

def test_strip_pii():
    payload = {
        "farm_id": "123",
        "phone": "555-1234",
        "farmer_name": "Test User",
        "domain": "crop"
    }
    cleaned = strip_pii(payload)
    assert "phone" not in cleaned
    assert "farmer_name" not in cleaned
    assert "farm_id" in cleaned
    assert "domain" in cleaned
