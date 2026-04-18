from application.use_cases.exceptions import UserNotFoundError
from domain.repositories.user_repository import UserRepository


class DeleteUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, user_id: str) -> None:
        user = await self._user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        await self._user_repo.delete(user_id)
