from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import (
    TransportCompany,
    Bus,
    Trip,
    Seat,
    Reservation,
)

from app.domain.schemas import (
    CompanyCreateRequest,
    BusCreateRequest,
    TripCreateRequest,
    ReservationCreateRequest
)
from app.domain.enums import SeatGenderType, ReservationStatus

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

        seats = []

        for seat_number in range(1, data.capacity + 1):

            seat = Seat(
                seat_number=seat_number,
                bus_id=bus.id,
                is_reservable=True,
                gender_type=SeatGenderType.NONE,
            )

            seats.append(seat)

        self.session.add_all(seats)

        await self.session.commit()

        await self.session.refresh(bus)

        return bus

    async def get_bus_by_id(
        self,
        bus_id: UUID,
    ) -> Bus | None:

        stmt = select(Bus).where(
            Bus.id == bus_id
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

    async def list_trips(
        self,
    ) -> list[Trip]:

        stmt = select(Trip)

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    
    async def get_trip_by_id(
        self,
        trip_id: UUID,
    ) -> Trip | None:

        stmt = select(Trip).where(
            Trip.id == trip_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    
    async def get_seat_by_id(
        self,
        seat_id: UUID,
    ) -> Seat | None:

        stmt = select(Seat).where(
            Seat.id == seat_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    
    async def get_reservation(
        self,
        trip_id: UUID,
        seat_id: UUID,
    ) -> Reservation | None:

        stmt = select(Reservation).where(
            Reservation.trip_id == trip_id,
            Reservation.seat_id == seat_id,
            Reservation.status == ReservationStatus.RESERVED,
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    
    async def create_reservation(
        self,
        passenger_id: UUID,
        data: ReservationCreateRequest,
    ) -> Reservation:

        reservation = Reservation(
            passenger_id=passenger_id,
            trip_id=data.trip_id,
            seat_id=data.seat_id,
        )

        self.session.add(reservation)

        await self.session.commit()

        await self.session.refresh(reservation)

        return reservation