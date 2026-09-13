import pytest
from src.zone3_memory.db.auth import login, signup
from src.zone3_memory.db import farm_memory
import os
from pathlib import Path

test_db = Path("test_auth.db")
_orig_db_path = None

def setup_module():
    global _orig_db_path
    _orig_db_path = farm_memory.DEFAULT_DB_PATH
    farm_memory.DEFAULT_DB_PATH = test_db
    if test_db.exists():
        test_db.unlink()
    farm_memory.init_db()

def teardown_module():
    if test_db.exists():
        try:
            test_db.unlink()
        except PermissionError:
            pass
    farm_memory.DEFAULT_DB_PATH = _orig_db_path

def test_auth_flow():
    # Signup
    f_id = signup("5551234", "1234", "Test Farmer")
    assert f_id is not None
    
    # Login success
    assert login("5551234", "1234") == f_id
    
    # Login fail
    assert login("5551234", "9999") is None
    
    # Duplicate signup
    with pytest.raises(ValueError):
        signup("5551234", "5678", "Other")
