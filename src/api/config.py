"""Runtime settings for the API, read once from the environment (.env is loaded in main)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _flag(name: str, default: str) -> bool:
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    # HMAC secret for session tokens. The default is for local demos only.
    secret_key: str = field(default_factory=lambda: os.environ.get("AGRIVISION_API_SECRET", "agrivision-dev-secret-change-me"))
    token_ttl_seconds: int = field(default_factory=lambda: int(os.environ.get("AGRIVISION_TOKEN_TTL", str(7 * 24 * 3600))))
    # DEMO: the OTP is returned in the API response so the web UI can show it on screen.
    demo_otp: bool = field(default_factory=lambda: _flag("AGRIVISION_DEMO_OTP", "true"))
    otp_ttl_seconds: int = 300
    cors_origins: tuple[str, ...] = field(default_factory=lambda: tuple(
        o.strip() for o in os.environ.get(
            "AGRIVISION_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",") if o.strip()
    ))
    expert_mode: str = field(default_factory=lambda: os.environ.get("AGRIVISION_EXPERT_MODE", "auto"))
    voice_enabled: bool = field(default_factory=lambda: _flag("VOICE_INPUT_ENABLED", "false"))
    # Admin portal login. The default password is for local demos only — set ADMIN_PASSWORD when deploying.
    admin_username: str = field(default_factory=lambda: os.environ.get("ADMIN_USERNAME", "admin"))
    admin_password: str = field(default_factory=lambda: os.environ.get("ADMIN_PASSWORD", "agrivision-admin"))
    admin_token_ttl_seconds: int = 12 * 3600
    upload_dir: Path = PROJECT_ROOT / "results" / "api_uploads"
    max_upload_bytes: int = 10 * 1024 * 1024


settings = Settings()
