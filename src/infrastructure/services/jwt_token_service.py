import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from domain.services.token_service import TokenPayload, TokenService
from infrastructure.config.settings import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class JWTTokenService(TokenService):
    def create_access_token(self, user_id: str) -> str:
        return self._encode(
            user_id,
            ACCESS_TOKEN_TYPE,
            timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    def create_refresh_token(self, user_id: str) -> str:
        return self._encode(
            user_id,
            REFRESH_TOKEN_TYPE,
            timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

    def decode_token(self, token: str) -> Optional[TokenPayload]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return TokenPayload(
                user_id=payload["sub"],
                jti=payload["jti"],
                token_type=payload["type"],
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
        except (jwt.PyJWTError, KeyError):
            return None

    @staticmethod
    def _encode(user_id: str, token_type: str, delta: timedelta) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": user_id,
            "type": token_type,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + delta,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
