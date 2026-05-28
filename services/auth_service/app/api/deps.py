from uuid import UUID

from jose import JWTError

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.infrastructure.repositories import UserRepository
from app.domain.services import AuthService

from app.infrastructure.security import decode_access_token
from app.infrastructure.models import User


async def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:

    user_repository = UserRepository(db)

    return AuthService(user_repository)


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user_repository = UserRepository(db)

    user = await user_repository.get_user_by_id(
        UUID(user_id)
    )

    if user is None:
        raise credentials_exception

    return user