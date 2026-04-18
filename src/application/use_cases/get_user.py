from application.use_cases.exceptions import UserNotFoundError
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, user_id: str) -> User:
        user = await self._user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user


class ListUsersUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self._user_repo.find_all(skip=skip, limit=limit)
