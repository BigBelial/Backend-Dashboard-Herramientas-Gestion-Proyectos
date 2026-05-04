from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.entities.role import Role


@dataclass
class UpdateUserDTO:
    user_id: str
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None
    role: Optional[Role] = None
