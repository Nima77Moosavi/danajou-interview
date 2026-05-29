from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.enums import SeatHoldStatus
from app.domain.schemas import (
    BusCreateRequest,
    CompanyCreateRequest,
    InternalSeatHoldRequest,
    SeatUpdateRequest,
    TripCreateRequest,
)
from app.infrastructure.models import Bus, Seat, SeatHold, TransportCompany, Trip


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

    async def list_trips(self) -> list[Trip]:
        ...

    async def search_trips(
        self,
        origin: str | None,
        destination: str | None,
        departure_date: date | None,
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

    async def update_seat(
        self,
        seat: Seat,
        data: SeatUpdateRequest,
    ) -> Seat:
        ...

    async def create_seat_hold(
        self,
        data: InternalSeatHoldRequest,
    ) -> SeatHold:
        ...

    async def get_seat_hold_by_reservation_id(
        self,
        reservation_id: UUID,
    ) -> SeatHold | None:
        ...

    async def update_seat_hold_status(
        self,
        hold: SeatHold,
        status: SeatHoldStatus,
    ) -> SeatHold:
        ...

    async def count_remaining_capacity(
        self,
        trip: Trip,
    ) -> int:
        ...
