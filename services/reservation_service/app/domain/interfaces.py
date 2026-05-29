from typing import Protocol
from uuid import UUID

from app.domain.enums import ReservationStatus
from app.infrastructure.models import Reservation


class IReservationRepository(Protocol):
    async def create_reservation(
        self,
        reservation_id: UUID,
        passenger_id: UUID,
        passenger_gender: str,
        trip_id: UUID,
        seat_id: UUID,
    ) -> Reservation:
        ...

    async def get_by_id(
        self,
        reservation_id: UUID,
    ) -> Reservation | None:
        ...

    async def update_status(
        self,
        reservation: Reservation,
        status: ReservationStatus,
    ) -> Reservation:
        ...
