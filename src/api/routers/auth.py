"""Phone + OTP signup, phone + PIN login."""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from src.api import otp, repository
from src.api.config import settings
from src.api.security import issue_token, read_token
from src.zone3_memory.db import auth

router = APIRouter(prefix="/auth", tags=["auth"])

_PHONE_RE = re.compile(r"^[6-9]\d{9}$")  # Indian mobile number, without +91


def _normalize_phone(v: str) -> str:
    digits = re.sub(r"\D", "", v or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if not _PHONE_RE.match(digits):
        raise ValueError("Enter a valid 10-digit mobile number.")
    return digits


class PhoneIn(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        return _normalize_phone(v)


class OtpVerifyIn(PhoneIn):
    code: str


class SignupIn(BaseModel):
    verification_token: str
    name: str
    pin: str

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = " ".join(v.split())
        if not 2 <= len(v) <= 60:
            raise ValueError("Please enter your name.")
        return v

    @field_validator("pin")
    @classmethod
    def _pin(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}", v):
            raise ValueError("PIN must be 4 digits.")
        return v


class LoginIn(PhoneIn):
    pin: str


def _session(farm_id: str) -> dict:
    profile = repository.get_profile(farm_id)
    return {"token": issue_token({"typ": "session", "sub": farm_id}), "farmer": profile}


@router.post("/otp/request")
def request_otp(body: PhoneIn) -> dict:
    code = otp.issue(body.phone)
    return {
        "sent": True,
        "expires_in": settings.otp_ttl_seconds,
        "registered": repository.phone_exists(body.phone),
        # DEMO ONLY — see src/api/otp.py
        "demo_otp": code if settings.demo_otp else None,
    }


@router.post("/otp/verify")
def verify_otp(body: OtpVerifyIn) -> dict:
    if not otp.verify(body.phone, body.code.strip()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect or expired code.")
    return {"verification_token": issue_token({"typ": "otp", "sub": body.phone}, ttl=900)}


@router.post("/signup")
def signup(body: SignupIn) -> dict:
    claims = read_token(body.verification_token)
    if not claims or claims.get("typ") != "otp":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Phone verification expired. Please request a new code.")
    try:
        farm_id = auth.signup(claims["sub"], body.pin, body.name)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e)) from e
    return _session(farm_id)


@router.post("/login")
def login(body: LoginIn) -> dict:
    farm_id = auth.login(body.phone, body.pin)
    if not farm_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Phone number or PIN is incorrect.")
    return _session(farm_id)
