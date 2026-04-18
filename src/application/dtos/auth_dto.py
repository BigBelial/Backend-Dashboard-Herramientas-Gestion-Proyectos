from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from domain.entities.role import Role


@dataclass
class RegisterDTO:
    email: str
    password: str
    full_name: str
    role: Role = Role.CONSULTOR
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class TokenDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class RefreshTokenDTO:
    refresh_token: str


@dataclass
class LogoutDTO:
    access_token: str
