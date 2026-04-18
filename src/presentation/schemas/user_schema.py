from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
