from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from domain.entities.role import Role


@dataclass
class User:
    email: str
    hashed_password: str
    full_name: str
    is_active: bool = True
    role: Role = Role.CONSULTOR
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[str] = None
