from app.domain.interfaces import (
    ITransportRepository,
)

from app.domain.schemas import (
    BusCreateRequest,
    TripCreateRequest,
)


class TransportService:
    def __init__(
        self,
        repository: ITransportRepository,
    ):
        self.repository = repository

    async def create_bus(
        self,
        data: BusCreateRequest,
    ):
        return await self.repository.create_bus(data)

    async def create_trip(
        self,
        data: TripCreateRequest,
    ):
        return await self.repository.create_trip(data)

    async def list_trips(
        self,
    ):
        return await self.repository.list_trips()