from datetime import datetime

from application.dtos.user_dto import UpdateUserDTO
from application.use_cases.exceptions import UserAlreadyExistsError, UserNotFoundError
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.services.password_service import PasswordService


class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepository, password_svc: PasswordService):
        self._user_repo = user_repo
        self._password_svc = password_svc

    async def execute(self, dto: UpdateUserDTO) -> User:
        user = await self._user_repo.find_by_id(dto.user_id)
        if not user:
            raise UserNotFoundError(dto.user_id)

        if dto.email and dto.email != user.email:
            existing = await self._user_repo.find_by_email(dto.email)
            if existing:
                raise UserAlreadyExistsError(dto.email)
            user.email = dto.email

        if dto.password:
            user.hashed_password = self._password_svc.hash(dto.password)

        if dto.is_active is not None:
            user.is_active = dto.is_active

        user.updated_at = datetime.utcnow()
        return await self._user_repo.update(user)
