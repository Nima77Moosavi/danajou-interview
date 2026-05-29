from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ReservationStatus
from app.domain.interfaces import IReservationRepository
from app.infrastructure.models import Reservation


class ReservationRepository(IReservationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reservation(
        self,
        reservation_id: UUID,
        passenger_id: UUID,
        passenger_gender: str,
        trip_id: UUID,
        seat_id: UUID,
    ) -> Reservation:
        reservation = Reservation(
            id=reservation_id,
            passenger_id=passenger_id,
            passenger_gender=passenger_gender,
            trip_id=trip_id,
            seat_id=seat_id,
            status=ReservationStatus.PENDING,
        )

        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)

        return reservation

    async def get_by_id(
        self,
        reservation_id: UUID,
    ) -> Reservation | None:
        stmt = select(Reservation).where(Reservation.id == reservation_id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def update_status(
        self,
        reservation: Reservation,
        status: ReservationStatus,
    ) -> Reservation:
        reservation.status = status

        await self.session.commit()
        await self.session.refresh(reservation)

        return reservation
