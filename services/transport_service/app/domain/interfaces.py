from typing import Protocol
from uuid import UUID

from app.infrastructure.models import (
    TransportCompany,
    Bus,
    Trip,
    Reservation,
    Seat,
)

from app.domain.schemas import (
    CompanyCreateRequest,
    BusCreateRequest,
    TripCreateRequest,
    ReservationCreateRequest
)


class ITransportRepository(Protocol):

    async def create_company(
        self,
        owner_id: UUID,
        data: CompanyCreateRequest,
    ) -> TransportCompany:
        ...

    async def get_company_by_owner(
        self,
        owner_id: UUID,
    ) -> TransportCompany | None:
        ...

    async def get_company_by_id(
        self,
        company_id: UUID,
    ) -> TransportCompany | None:
        ...

    async def create_bus(
        self,
        data: BusCreateRequest,
    ) -> Bus:
        ...

    async def get_bus_by_id(
        self,
        bus_id: UUID,
    ) -> Bus | None:
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

    async def get_trip_by_id(
        self,
        trip_id: UUID,
    ) -> Trip | None:
        ...

    async def get_seat_by_id(
        self,
        seat_id: UUID,
    ) -> Seat | None:
        ...

    async def get_reservation(
        self,
        trip_id: UUID,
        seat_id: UUID,
    ) -> Reservation | None:
        ...

    async def create_reservation(
        self,
        passenger_id: UUID,
        data: ReservationCreateRequest,
    ) -> Reservation:
        ...
