from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services import SearchService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import SearchRepository


async def get_search_service(
    db: AsyncSession = Depends(get_db),
) -> SearchService:
    return SearchService(SearchRepository(db))
