from app.domain.schemas import CurrentUser
from app.infrastructure.security import decode_access_token
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from jose import JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db

from app.infrastructure.repositories import (
    TransportRepository,
)

from app.domain.services import (
    TransportService,
)


async def get_transport_service(
    db: AsyncSession = Depends(get_db),
) -> TransportService:

    repository = TransportRepository(db)

    return TransportService(repository)


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise credentials_exception

        return CurrentUser(
            user_id=user_id,
            role=role,
        )

    except JWTError:
        raise credentials_exception
