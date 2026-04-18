from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    role: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
