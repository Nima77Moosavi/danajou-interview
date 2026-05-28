from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas import (
    UserRegisterRequest,
    UserResponse,
    LoginRequest,
    TokenResponse,
)
from app.infrastructure.models import User

from app.domain.services import AuthService

from app.infrastructure.database import get_db
from app.api.deps import get_auth_service, get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):

    return await auth_service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):

    return await auth_service.login(data)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user: User = Depends(get_current_user),
):

    return current_user
