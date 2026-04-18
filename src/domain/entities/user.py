from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from domain.entities.role import Role


@dataclass
class User:
    email: str
    hashed_password: str
    is_active: bool = True
    role: Role = Role.CONSULTOR
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[str] = None
