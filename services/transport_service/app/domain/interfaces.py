from typing import Protocol

from app.infrastructure.models import (
    Bus,
    Trip,
)

from app.domain.schemas import (
    BusCreateRequest,
    TripCreateRequest,
)


class ITransportRepository(Protocol):

    async def create_bus(
        self,
        data: BusCreateRequest,
    ) -> Bus:
        ...

    async def create_trip(
        self,
        data: TripCreateRequest,
    ) -> Trip:
        ...

    async def list_trips(
        self,
    ) -> list[Trip]:
        ...