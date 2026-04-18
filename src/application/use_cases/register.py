from datetime import datetime

from application.dtos.auth_dto import RegisterDTO
from application.use_cases.exceptions import UserAlreadyExistsError
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.services.password_service import PasswordService


class RegisterUseCase:
    def __init__(self, user_repo: UserRepository, password_svc: PasswordService):
        self._user_repo = user_repo
        self._password_svc = password_svc

    async def execute(self, dto: RegisterDTO) -> User:
        if await self._user_repo.find_by_email(dto.email):
            raise UserAlreadyExistsError(dto.email)

        user = User(
            email=dto.email,
            hashed_password=self._password_svc.hash(dto.password),
            full_name=dto.full_name,
            is_active=True,
            role=dto.role,
            phone=dto.phone,
            birth_date=dto.birth_date,
            location=dto.location,
            country=dto.country,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return await self._user_repo.save(user)
