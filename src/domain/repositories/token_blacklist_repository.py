from abc import ABC, abstractmethod
from datetime import datetime


class TokenBlacklistRepository(ABC):
    @abstractmethod
    async def add(self, jti: str, expires_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_blacklisted(self, jti: str) -> bool:
        raise NotImplementedError
