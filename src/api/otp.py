"""
In-memory OTP store for phone verification.

DEMO ONLY: codes live in process memory and, when AGRIVISION_DEMO_OTP is on,
are returned to the client instead of being sent by SMS. To go live, replace
`deliver()` with an SMS provider call and turn the demo flag off.
"""

from __future__ import annotations

import secrets
import threading
import time

from src.api.config import settings

_MAX_ATTEMPTS = 5
_lock = threading.Lock()
_codes: dict[str, tuple[str, float, int]] = {}  # phone -> (code, expires_at, attempts)


def issue(phone: str) -> str:
    code = f"{secrets.randbelow(10**6):06d}"
    with _lock:
        _codes[phone] = (code, time.time() + settings.otp_ttl_seconds, 0)
    deliver(phone, code)
    return code


def deliver(phone: str, code: str) -> None:
    """SMS hook. Intentionally a no-op in demo mode."""


def verify(phone: str, code: str) -> bool:
    with _lock:
        entry = _codes.get(phone)
        if not entry:
            return False
        expected, expires_at, attempts = entry
        if time.time() > expires_at or attempts >= _MAX_ATTEMPTS:
            _codes.pop(phone, None)
            return False
        if not secrets.compare_digest(expected, code):
            _codes[phone] = (expected, expires_at, attempts + 1)
            return False
        _codes.pop(phone, None)
        return True
