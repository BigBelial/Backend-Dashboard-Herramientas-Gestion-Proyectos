from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from domain.entities.role import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class AdminRegisterRequest(RegisterRequest):
    role: Role = Role.CONSULTOR


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
