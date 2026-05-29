import logging

import httpx
from fastapi import HTTPException, status

from app.domain.interfaces import IUserRepository

from app.domain.enums import UserRole
from app.domain.schemas import (
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    TokenResponse,
    UserRegisterRequest,
)
from app.infrastructure.database import settings
from app.infrastructure.messaging import RabbitMQEventBus

from app.infrastructure.security import (
    create_access_token,
    hash_password,
    verify_password,
)


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        event_bus: RabbitMQEventBus | None = None,
    ):
        self.user_repository = user_repository
        self.event_bus = event_bus or RabbitMQEventBus()

    async def register(
        self,
        data: UserRegisterRequest,
    ):

        existing_user = await self.user_repository.get_user_by_phone_number(
            data.phone_number
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists",
            )

        if data.role != UserRole.PASSENGER and not data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required for admin and transport owner users",
            )

        password_hash = hash_password(data.password) if data.password else None

        user = await self.user_repository.create_user(
            phone_number=data.phone_number,
            password_hash=password_hash,
            gender=data.gender,
            role=data.role,
            is_active=True,
        )

        return user

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:

        user = await self.user_repository.get_user_by_phone_number(
            data.phone_number
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Use OTP authentication for this account",
            )

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = self._create_user_token(user)

        return TokenResponse(
            access_token=access_token
        )

    async def request_otp(
        self,
        data: OTPRequest,
    ) -> None:
        existing_user = await self.user_repository.get_user_by_phone_number(
            data.phone_number
        )

        gender = existing_user.gender if existing_user else data.gender

        await self.event_bus.publish(
            "otp.requested",
            {
                "phone_number": data.phone_number,
                "gender": gender.value,
            },
        )

        logger.info("otp requested", extra={"phone_number": data.phone_number})

    async def verify_otp(
        self,
        data: OTPVerifyRequest,
    ) -> TokenResponse:
        verify_url = f"{settings.NOTIFICATION_SERVICE_URL}/internal/otp/verify"

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(
                    verify_url,
                    auth=(
                        settings.NOTIFICATION_SERVICE_USERNAME,
                        settings.NOTIFICATION_SERVICE_PASSWORD,
                    ),
                    json={
                        "phone_number": data.phone_number,
                        "code": data.code,
                    },
                )
            except httpx.HTTPError as exc:
                logger.exception("notification service otp verify failed")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Notification service is unavailable",
                ) from exc

        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP",
            )

        user = await self.user_repository.get_user_by_phone_number(
            data.phone_number
        )

        if user is None:
            user = await self.user_repository.create_user(
                phone_number=data.phone_number,
                password_hash=None,
                gender=data.gender,
                role=UserRole.PASSENGER,
                is_active=True,
            )

        return TokenResponse(access_token=self._create_user_token(user))

    @staticmethod
    def _create_user_token(user) -> str:
        return create_access_token(
            user_id=str(user.id),
            role=user.role.value,
            gender=user.gender.value,
            phone_number=user.phone_number,
        )
