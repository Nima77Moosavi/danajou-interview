from datetime import date
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import SeatGenderType, SeatHoldStatus
from app.domain.interfaces import ITransportRepository
from app.domain.schemas import (
    BusCreateRequest,
    CompanyCreateRequest,
    InternalSeatHoldRequest,
    SeatUpdateRequest,
    TripCreateRequest,
)
from app.infrastructure.models import (
    Bus,
    Seat,
    SeatHold,
    TransportCompany,
    Trip,
)


class TransportRepository(ITransportRepository):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create_company(
        self,
        owner_id: UUID,
        data: CompanyCreateRequest,
    ) -> TransportCompany:
        company = TransportCompany(
            name=data.name,
            owner_id=owner_id,
        )

        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)

        return company

    async def get_company_by_owner(
        self,
        owner_id: UUID,
    ) -> TransportCompany | None:
        stmt = select(TransportCompany).where(
            TransportCompany.owner_id == owner_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_company_by_id(
        self,
        company_id: UUID,
    ) -> TransportCompany | None:
        stmt = select(TransportCompany).where(
            TransportCompany.id == company_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_bus(
        self,
        data: BusCreateRequest,
    ) -> Bus:
        bus = Bus(
            plate_number=data.plate_number,
            capacity=data.capacity,
            company_id=data.company_id,
        )

        self.session.add(bus)
        await self.session.flush()

        seats = [
            Seat(
                seat_number=seat_number,
                bus_id=bus.id,
                is_reservable=True,
                gender_type=SeatGenderType.NONE,
            )
            for seat_number in range(1, data.capacity + 1)
        ]

        self.session.add_all(seats)
        await self.session.commit()

        stmt = (
            select(Bus)
            .where(Bus.id == bus.id)
            .options(selectinload(Bus.seats))
        )
        result = await self.session.execute(stmt)

        return result.scalar_one()

    async def get_bus_by_id(
        self,
        bus_id: UUID,
    ) -> Bus | None:
        stmt = (
            select(Bus)
            .where(Bus.id == bus_id)
            .options(
                selectinload(Bus.company),
                selectinload(Bus.seats),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_trip(
        self,
        data: TripCreateRequest,
    ) -> Trip:
        trip = Trip(**data.model_dump())

        self.session.add(trip)
        await self.session.commit()
        await self.session.refresh(trip)

        return trip

    async def list_trips(self) -> list[Trip]:
        result = await self.session.execute(self._trip_query())

        return list(result.scalars().unique().all())

    async def search_trips(
        self,
        origin: str | None,
        destination: str | None,
        departure_date: date | None,
    ) -> list[Trip]:
        stmt = self._trip_query()

        if origin:
            stmt = stmt.where(Trip.origin.ilike(f"%{origin}%"))

        if destination:
            stmt = stmt.where(Trip.destination.ilike(f"%{destination}%"))

        if departure_date:
            stmt = stmt.where(func.date(Trip.departure_time) == departure_date)

        result = await self.session.execute(stmt.order_by(Trip.departure_time))

        return list(result.scalars().unique().all())

    async def get_trip_by_id(
        self,
        trip_id: UUID,
    ) -> Trip | None:
        stmt = self._trip_query().where(Trip.id == trip_id)
        result = await self.session.execute(stmt)

        return result.scalars().unique().one_or_none()

    async def get_seat_by_id(
        self,
        seat_id: UUID,
    ) -> Seat | None:
        stmt = (
            select(Seat)
            .where(Seat.id == seat_id)
            .options(selectinload(Seat.bus))
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def update_seat(
        self,
        seat: Seat,
        data: SeatUpdateRequest,
    ) -> Seat:
        if data.is_reservable is not None:
            seat.is_reservable = data.is_reservable

        if data.gender_type is not None:
            seat.gender_type = data.gender_type

        await self.session.commit()
        await self.session.refresh(seat)

        return seat

    async def create_seat_hold(
        self,
        data: InternalSeatHoldRequest,
    ) -> SeatHold:
        hold = SeatHold(
            reservation_id=data.reservation_id,
            trip_id=data.trip_id,
            seat_id=data.seat_id,
            status=SeatHoldStatus.HELD,
        )

        self.session.add(hold)
        await self.session.commit()
        await self.session.refresh(hold)

        return hold

    async def get_seat_hold_by_reservation_id(
        self,
        reservation_id: UUID,
    ) -> SeatHold | None:
        stmt = select(SeatHold).where(
            SeatHold.reservation_id == reservation_id
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def update_seat_hold_status(
        self,
        hold: SeatHold,
        status: SeatHoldStatus,
    ) -> SeatHold:
        hold.status = status

        await self.session.commit()
        await self.session.refresh(hold)

        return hold

    async def count_remaining_capacity(
        self,
        trip: Trip,
    ) -> int:
        reservable_seats = sum(1 for seat in trip.bus.seats if seat.is_reservable)
        active_holds = sum(
            1
            for hold in trip.holds
            if hold.status in {SeatHoldStatus.HELD, SeatHoldStatus.CONFIRMED}
        )

        return max(reservable_seats - active_holds, 0)

    @staticmethod
    def _trip_query() -> Select[tuple[Trip]]:
        return select(Trip).options(
            selectinload(Trip.bus).selectinload(Bus.company),
            selectinload(Trip.bus).selectinload(Bus.seats),
            selectinload(Trip.holds),
        )
