from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateUserDTO:
    user_id: str
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
