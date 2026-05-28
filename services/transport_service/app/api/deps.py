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