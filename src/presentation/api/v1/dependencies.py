from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from application.use_cases.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    TokenRevokedError,
    UserNotFoundError,
)
from application.use_cases.get_current_user import GetCurrentUserUseCase
from domain.entities.role import Role
from domain.entities.user import User
from infrastructure.database.mongodb import get_database
from infrastructure.repositories.mongo_token_blacklist_repository import MongoTokenBlacklistRepository
from infrastructure.repositories.mongo_user_repository import MongoUserRepository
from infrastructure.services.bcrypt_password_service import BcryptPasswordService
from infrastructure.services.jwt_token_service import JWTTokenService

bearer_scheme = HTTPBearer()


def get_user_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> MongoUserRepository:
    return MongoUserRepository(db)


def get_blacklist_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> MongoTokenBlacklistRepository:
    return MongoTokenBlacklistRepository(db)


def get_password_svc() -> BcryptPasswordService:
    return BcryptPasswordService()


def get_token_svc() -> JWTTokenService:
    return JWTTokenService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: MongoUserRepository = Depends(get_user_repo),
    token_svc: JWTTokenService = Depends(get_token_svc),
    blacklist_repo: MongoTokenBlacklistRepository = Depends(get_blacklist_repo),
) -> User:
    use_case = GetCurrentUserUseCase(user_repo, token_svc, blacklist_repo)
    try:
        return await use_case.execute(credentials.credentials)
    except (InvalidTokenError, TokenRevokedError, UserNotFoundError, InactiveUserError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(*roles: Role) -> User:
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not allowed to perform this action",
            )
        return current_user
    return Depends(_check)
