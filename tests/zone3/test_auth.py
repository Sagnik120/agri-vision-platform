import pytest
from src.zone3_memory.db.auth import login, signup
from src.zone3_memory.db import farm_memory
import os
from pathlib import Path

# Override DB path for tests
test_db = Path("test_auth.db")
farm_memory.DEFAULT_DB_PATH = test_db

def setup_module():
    if test_db.exists():
        test_db.unlink()
    farm_memory.init_db()

def teardown_module():
    if test_db.exists():
        test_db.unlink()

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
