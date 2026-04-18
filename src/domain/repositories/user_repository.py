from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        raise NotImplementedError
