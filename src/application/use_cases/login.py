from application.dtos.auth_dto import LoginDTO, TokenDTO
from application.use_cases.exceptions import InactiveUserError, InvalidCredentialsError
from domain.repositories.user_repository import UserRepository
from domain.services.password_service import PasswordService
from domain.services.token_service import TokenService


class LoginUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        password_svc: PasswordService,
        token_svc: TokenService,
    ):
        self._user_repo = user_repo
        self._password_svc = password_svc
        self._token_svc = token_svc

    async def execute(self, dto: LoginDTO) -> TokenDTO:
        user = await self._user_repo.find_by_email(dto.email)
        if not user or not self._password_svc.verify(dto.password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        return TokenDTO(
            access_token=self._token_svc.create_access_token(user.id),
            refresh_token=self._token_svc.create_refresh_token(user.id),
        )
