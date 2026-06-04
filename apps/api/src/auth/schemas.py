"""Auth request/response schemas (login, register, reset, verify)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"email": "jane@example.com", "password": "…"}]}
    )


class ForgotRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=12, max_length=256)


class VerifyResendRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    """Returned by ``POST /v1/auth/login``. The cookie is set in headers."""

    ok: bool = True


__all__ = [
    "ForgotRequest",
    "LoginRequest",
    "LoginResponse",
    "ResetRequest",
    "VerifyResendRequest",
]
