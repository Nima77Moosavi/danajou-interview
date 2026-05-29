from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas import CurrentUser
from app.domain.services import ReservationService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import ReservationRepository
from app.infrastructure.security import decode_access_token


security = HTTPBearer()


async def get_reservation_service(
    db: AsyncSession = Depends(get_db),
) -> ReservationService:
    return ReservationService(ReservationRepository(db))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_access_token(credentials.credentials)

        user_id = payload.get("sub")
        role = payload.get("role")
        gender = payload.get("gender")

        if not user_id or not role or not gender:
            raise credentials_exception

        return CurrentUser(
            user_id=UUID(user_id),
            role=role,
            gender=gender,
        )
    except (JWTError, ValueError):
        raise credentials_exception
