from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.dtos.response_dto import ResponseDTO
from application.dtos.user_dto import UpdateUserDTO
from application.use_cases.delete_user import DeleteUserUseCase
from application.use_cases.exceptions import UserAlreadyExistsError, UserNotFoundError
from application.use_cases.get_user import GetUserUseCase, ListUsersUseCase
from application.use_cases.update_user import UpdateUserUseCase
from domain.entities.user import User
from presentation.api.v1.dependencies import (
    get_current_user,
    get_password_svc,
    get_user_repo,
    require_roles,
)
from domain.entities.role import Role
from presentation.schemas.user_schema import UpdateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        role=user.role.value,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/", response_model=ResponseDTO[list[UserResponse]])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_repo=Depends(get_user_repo),
    _: User = require_roles(Role.ADMIN),
):
    users = await ListUsersUseCase(user_repo).execute(skip=skip, limit=limit)
    return ResponseDTO(
        status_code=status.HTTP_200_OK,
        message="Users retrieved successfully",
        data=[_user_response(u) for u in users],
    )


@router.get("/{user_id}", response_model=ResponseDTO[UserResponse])
async def get_user(
    user_id: str,
    user_repo=Depends(get_user_repo),
    _: User = Depends(get_current_user),
):
    try:
        user = await GetUserUseCase(user_repo).execute(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ResponseDTO(
        status_code=status.HTTP_200_OK,
        message="User retrieved successfully",
        data=_user_response(user),
    )


@router.put("/{user_id}", response_model=ResponseDTO[UserResponse])
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    user_repo=Depends(get_user_repo),
    password_svc=Depends(get_password_svc),
    _: User = Depends(get_current_user),
):
    try:
        user = await UpdateUserUseCase(user_repo, password_svc).execute(
            UpdateUserDTO(
                user_id=user_id,
                email=body.email,
                password=body.password,
                is_active=body.is_active,
            )
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return ResponseDTO(
        status_code=status.HTTP_200_OK,
        message="User updated successfully",
        data=_user_response(user),
    )


@router.delete("/{user_id}", response_model=ResponseDTO[None])
async def delete_user(
    user_id: str,
    user_repo=Depends(get_user_repo),
    _: User = Depends(get_current_user),
):
    try:
        await DeleteUserUseCase(user_repo).execute(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return ResponseDTO(status_code=status.HTTP_200_OK, message="User deleted successfully")
