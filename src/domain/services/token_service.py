from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TokenPayload:
    user_id: str
    jti: str
    token_type: str
    expires_at: datetime


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str) -> Optional[TokenPayload]:
        raise NotImplementedError
