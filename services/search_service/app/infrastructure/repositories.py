from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SearchQuery


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_search(
        self,
        origin: str | None,
        destination: str | None,
        departure_date: date | None,
        result_count: int,
    ) -> SearchQuery:
        query = SearchQuery(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            result_count=result_count,
        )

        self.session.add(query)
        await self.session.commit()
        await self.session.refresh(query)

        return query
