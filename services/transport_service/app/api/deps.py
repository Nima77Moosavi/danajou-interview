from app.domain.schemas import CurrentUser
from app.infrastructure.security import decode_access_token
from app.infrastructure.security import validate_service_credentials
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from jose import JWTError
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
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
service_security = HTTPBasic()


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
        gender = payload.get("gender")

        if not user_id or not role:
            raise credentials_exception

        return CurrentUser(
            user_id=user_id,
            role=role,
            gender=gender,
        )

    except (JWTError, ValueError):
        raise credentials_exception


async def require_service_auth(
    credentials: HTTPBasicCredentials = Depends(service_security),
) -> str:
    if not validate_service_credentials(
        credentials.username,
        credentials.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
