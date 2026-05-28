from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import (
    Bus,
    Trip,
)

from app.domain.schemas import (
    BusCreateRequest,
    TripCreateRequest,
)

from app.domain.interfaces import (
    ITransportRepository,
)


class TransportRepository(
    ITransportRepository
):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create_bus(
        self,
        data: BusCreateRequest,
    ) -> Bus:

        bus = Bus(**data.model_dump())

        self.session.add(bus)

        await self.session.commit()

        await self.session.refresh(bus)

        return bus

    async def create_trip(
        self,
        data: TripCreateRequest,
    ) -> Trip:

        trip = Trip(**data.model_dump())

        self.session.add(trip)

        await self.session.commit()

        await self.session.refresh(trip)

        return trip

    async def list_trips(
        self,
    ) -> list[Trip]:

        stmt = select(Trip)

        result = await self.session.execute(stmt)

        return list(result.scalars().all())