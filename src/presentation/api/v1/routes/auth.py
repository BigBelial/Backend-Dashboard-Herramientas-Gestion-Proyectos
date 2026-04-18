from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.dtos.auth_dto import LoginDTO, LogoutDTO, RefreshTokenDTO, RegisterDTO
from application.dtos.response_dto import ResponseDTO
from application.use_cases.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenRevokedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from application.use_cases.login import LoginUseCase
from application.use_cases.logout import LogoutUseCase
from application.use_cases.refresh_token import RefreshTokenUseCase
from application.use_cases.register import RegisterUseCase
from domain.entities.user import User
from presentation.api.v1.dependencies import (
    get_blacklist_repo,
    get_current_user,
    get_password_svc,
    get_token_svc,
    get_user_repo,
)
from presentation.schemas.auth_schema import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from presentation.schemas.user_schema import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        role=user.role.value,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/register", response_model=ResponseDTO[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    user_repo=Depends(get_user_repo),
    password_svc=Depends(get_password_svc),
):
    try:
        user = await RegisterUseCase(user_repo, password_svc).execute(
            RegisterDTO(email=body.email, password=body.password)
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return ResponseDTO(
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=_user_response(user),
    )


@router.post("/login", response_model=ResponseDTO[TokenResponse])
async def login(
    body: LoginRequest,
    user_repo=Depends(get_user_repo),
    password_svc=Depends(get_password_svc),
    token_svc=Depends(get_token_svc),
):
    try:
        token = await LoginUseCase(user_repo, password_svc, token_svc).execute(
            LoginDTO(email=body.email, password=body.password)
        )
    except (InvalidCredentialsError, InactiveUserError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return ResponseDTO(
        status_code=status.HTTP_200_OK,
        message="Login successful",
        data=TokenResponse(access_token=token.access_token, refresh_token=token.refresh_token),
    )


@router.post("/logout", response_model=ResponseDTO[None])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    blacklist_repo=Depends(get_blacklist_repo),
    token_svc=Depends(get_token_svc),
):
    try:
        await LogoutUseCase(blacklist_repo, token_svc).execute(
            LogoutDTO(access_token=credentials.credentials)
        )
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return ResponseDTO(status_code=status.HTTP_200_OK, message="Logout successful")


@router.post("/refresh", response_model=ResponseDTO[TokenResponse])
async def refresh(
    body: RefreshTokenRequest,
    user_repo=Depends(get_user_repo),
    token_svc=Depends(get_token_svc),
    blacklist_repo=Depends(get_blacklist_repo),
):
    try:
        token = await RefreshTokenUseCase(user_repo, token_svc, blacklist_repo).execute(
            RefreshTokenDTO(refresh_token=body.refresh_token)
        )
    except (InvalidTokenError, TokenRevokedError, UserNotFoundError, InactiveUserError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return ResponseDTO(
        status_code=status.HTTP_200_OK,
        message="Token refreshed successfully",
        data=TokenResponse(access_token=token.access_token, refresh_token=token.refresh_token),
    )


@router.get("/me", response_model=ResponseDTO[UserResponse])
async def me(current_user: User = Depends(get_current_user)):
    return ResponseDTO(
        status_code=status.HTTP_200_OK,
        message="User retrieved successfully",
        data=_user_response(current_user),
    )
