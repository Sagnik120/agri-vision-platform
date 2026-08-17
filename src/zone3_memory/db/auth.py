import sqlite3
import uuid
from src.zone3_memory.db.farm_memory import DEFAULT_DB_PATH

def _get_conn():
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DEFAULT_DB_PATH)

def signup(phone: str, pin: str, name: str) -> str:
    """Create a new farmer and return their farmer_id."""
    conn = _get_conn()
    c = conn.cursor()
    
    # Check if exists
    c.execute("SELECT farm_id FROM farm WHERE phone = ?", (phone,))
    existing = c.fetchone()
    if existing:
        conn.close()
        raise ValueError("Phone number already registered")
        
    farmer_id = str(uuid.uuid4())
    c.execute(
        "INSERT INTO farm (farm_id, phone, pin, farmer_name) VALUES (?, ?, ?, ?)",
        (farmer_id, phone, pin, name)
    )
    conn.commit()
    conn.close()
    return farmer_id

def login(phone: str, pin: str) -> str | None:
    """Return farmer_id if credentials are correct, else None."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT farm_id FROM farm WHERE phone = ? AND pin = ?", (phone, pin))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
