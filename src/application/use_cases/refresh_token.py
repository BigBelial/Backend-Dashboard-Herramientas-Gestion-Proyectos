from application.dtos.auth_dto import RefreshTokenDTO, TokenDTO
from application.use_cases.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    TokenRevokedError,
    UserNotFoundError,
)
from domain.repositories.token_blacklist_repository import TokenBlacklistRepository
from domain.repositories.user_repository import UserRepository
from domain.services.token_service import TokenService

REFRESH_TOKEN_TYPE = "refresh"


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        token_svc: TokenService,
        blacklist_repo: TokenBlacklistRepository,
    ):
        self._user_repo = user_repo
        self._token_svc = token_svc
        self._blacklist_repo = blacklist_repo

    async def execute(self, dto: RefreshTokenDTO) -> TokenDTO:
        payload = self._token_svc.decode_token(dto.refresh_token)
        if not payload or payload.token_type != REFRESH_TOKEN_TYPE:
            raise InvalidTokenError()

        if await self._blacklist_repo.is_blacklisted(payload.jti):
            raise TokenRevokedError()

        user = await self._user_repo.find_by_id(payload.user_id)
        if not user:
            raise UserNotFoundError(payload.user_id)
        if not user.is_active:
            raise InactiveUserError()

        # Rotate: blacklist old refresh token
        await self._blacklist_repo.add(payload.jti, payload.expires_at)

        return TokenDTO(
            access_token=self._token_svc.create_access_token(user.id),
            refresh_token=self._token_svc.create_refresh_token(user.id),
        )
