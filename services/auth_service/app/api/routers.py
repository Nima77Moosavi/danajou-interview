from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas import (
    LoginRequest,
    MessageResponse,
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)
from app.infrastructure.models import User

from app.domain.services import AuthService

from app.infrastructure.database import get_db
from app.api.deps import (
    get_auth_service,
    get_current_user,
    require_service_auth,
)


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


@router.post(
    "/otp/request",
    response_model=MessageResponse,
    status_code=202,
)
async def request_otp(
    data: OTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.request_otp(data)

    return MessageResponse(detail="OTP requested")


@router.post(
    "/otp/verify",
    response_model=TokenResponse,
)
async def verify_otp(
    data: OTPVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.verify_otp(data)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user: User = Depends(get_current_user),
):

    return current_user


@router.get("/internal/basic/validate")
async def validate_basic_auth(
    service_name: str = Depends(require_service_auth),
):
    return {
        "service": service_name,
        "valid": True,
    }
