from fastapi import HTTPException, status
from app.domain.interfaces import IUserRepository

from app.domain.enums import UserRole
from app.domain.schemas import (
    UserRegisterRequest,
    LoginRequest,
    TokenResponse,
)

from app.infrastructure.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

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

        password_hash = hash_password(data.password)

        user = await self.user_repository.create_user(
            phone_number=data.phone_number,
            password_hash=password_hash,
            gender=data.gender,
            role=UserRole.PASSENGER,
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

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(
            str(user.id)
        )

        return TokenResponse(
            access_token=access_token
        )
