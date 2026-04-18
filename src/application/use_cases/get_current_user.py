from application.use_cases.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    TokenRevokedError,
    UserNotFoundError,
)
from domain.entities.user import User
from domain.repositories.token_blacklist_repository import TokenBlacklistRepository
from domain.repositories.user_repository import UserRepository
from domain.services.token_service import TokenService

ACCESS_TOKEN_TYPE = "access"


class GetCurrentUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        token_svc: TokenService,
        blacklist_repo: TokenBlacklistRepository,
    ):
        self._user_repo = user_repo
        self._token_svc = token_svc
        self._blacklist_repo = blacklist_repo

    async def execute(self, token: str) -> User:
        payload = self._token_svc.decode_token(token)
        if not payload or payload.token_type != ACCESS_TOKEN_TYPE:
            raise InvalidTokenError()

        if await self._blacklist_repo.is_blacklisted(payload.jti):
            raise TokenRevokedError()

        user = await self._user_repo.find_by_id(payload.user_id)
        if not user:
            raise UserNotFoundError(payload.user_id)
        if not user.is_active:
            raise InactiveUserError()

        return user
