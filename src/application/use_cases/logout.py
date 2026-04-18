from application.dtos.auth_dto import LogoutDTO
from application.use_cases.exceptions import InvalidTokenError
from domain.repositories.token_blacklist_repository import TokenBlacklistRepository
from domain.services.token_service import TokenService

ACCESS_TOKEN_TYPE = "access"


class LogoutUseCase:
    def __init__(self, blacklist_repo: TokenBlacklistRepository, token_svc: TokenService):
        self._blacklist_repo = blacklist_repo
        self._token_svc = token_svc

    async def execute(self, dto: LogoutDTO) -> None:
        payload = self._token_svc.decode_token(dto.access_token)
        if not payload or payload.token_type != ACCESS_TOKEN_TYPE:
            raise InvalidTokenError()

        await self._blacklist_repo.add(payload.jti, payload.expires_at)
