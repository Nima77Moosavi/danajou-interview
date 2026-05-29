from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services import NotificationService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import OTPRepository
from app.infrastructure.security import validate_service_credentials


service_security = HTTPBasic()


async def get_notification_service(
    db: AsyncSession = Depends(get_db),
) -> NotificationService:
    return NotificationService(OTPRepository(db))


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
