import logging
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.enums import SeatGenderType, SeatHoldStatus, UserRole
from app.domain.interfaces import ITransportRepository
from app.domain.schemas import (
    BusCreateRequest,
    CompanyCreateRequest,
    CurrentUser,
    InternalSeatHoldRequest,
    InternalSeatHoldResponse,
    InternalTripResponse,
    SeatUpdateRequest,
    TripCreateRequest,
)
from app.infrastructure.messaging import RabbitMQEventBus


logger = logging.getLogger(__name__)


class TransportService:
    def __init__(
        self,
        repository: ITransportRepository,
        event_bus: RabbitMQEventBus | None = None,
    ):
        self.repository = repository
        self.event_bus = event_bus or RabbitMQEventBus()

    async def create_company(
        self,
        current_user: CurrentUser,
        data: CompanyCreateRequest,
    ):
        self._require_transport_owner(current_user)

        existing_company = await self.repository.get_company_by_owner(
            current_user.user_id
        )

        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner already has a company",
            )

        company = await self.repository.create_company(
            owner_id=current_user.user_id,
            data=data,
        )

        logger.info("transport company created", extra={"company_id": company.id})

        return company

    async def create_bus(
        self,
        current_user: CurrentUser,
        data: BusCreateRequest,
    ):
        self._require_transport_owner(current_user)

        company = await self.repository.get_company_by_id(data.company_id)

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

        if company.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this company",
            )

        bus = await self.repository.create_bus(data)

        logger.info("bus created", extra={"bus_id": bus.id})

        return bus

    async def create_trip(
        self,
        current_user: CurrentUser,
        data: TripCreateRequest,
    ):
        self._require_transport_owner(current_user)

        bus = await self.repository.get_bus_by_id(data.bus_id)

        if not bus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bus not found",
            )

        if bus.company.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this bus",
            )

        trip = await self.repository.create_trip(data)
        await self.event_bus.publish(
            "trip.created",
            {
                "trip_id": str(trip.id),
                "bus_id": str(trip.bus_id),
                "origin": trip.origin,
                "destination": trip.destination,
                "departure_time": trip.departure_time,
            },
        )

        logger.info("trip created", extra={"trip_id": trip.id})

        return trip

    async def list_trips(self):
        return await self.repository.list_trips()

    async def update_seat(
        self,
        current_user: CurrentUser,
        seat_id: UUID,
        data: SeatUpdateRequest,
    ):
        self._require_transport_owner(current_user)

        seat = await self.repository.get_seat_by_id(seat_id)

        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found",
            )

        bus = await self.repository.get_bus_by_id(seat.bus_id)

        if not bus or bus.company.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this seat",
            )

        updated = await self.repository.update_seat(seat, data)
        await self.event_bus.publish(
            "seat.updated",
            {
                "seat_id": str(updated.id),
                "bus_id": str(updated.bus_id),
                "is_reservable": updated.is_reservable,
                "gender_type": updated.gender_type.value,
            },
        )

        logger.info("seat updated", extra={"seat_id": updated.id})

        return updated

    async def search_trips(
        self,
        origin,
        destination,
        departure_date,
    ) -> list[InternalTripResponse]:
        trips = await self.repository.search_trips(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
        )

        responses: list[InternalTripResponse] = []

        for trip in trips:
            responses.append(
                InternalTripResponse(
                    id=trip.id,
                    origin=trip.origin,
                    destination=trip.destination,
                    departure_time=trip.departure_time,
                    arrival_time=trip.arrival_time,
                    price=trip.price,
                    bus_id=trip.bus_id,
                    company_name=trip.bus.company.name,
                    remaining_capacity=await self.repository.count_remaining_capacity(
                        trip
                    ),
                )
            )

        return responses

    async def hold_seat(
        self,
        data: InternalSeatHoldRequest,
    ) -> InternalSeatHoldResponse:
        trip = await self.repository.get_trip_by_id(data.trip_id)

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found",
            )

        seat = await self.repository.get_seat_by_id(data.seat_id)

        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found",
            )

        if seat.bus_id != trip.bus_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seat does not belong to trip bus",
            )

        if not seat.is_reservable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seat is not reservable",
            )

        if (
            seat.gender_type != SeatGenderType.NONE
            and seat.gender_type != data.passenger_gender
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passenger gender does not match seat restriction",
            )

        for hold in trip.holds:
            if (
                hold.seat_id == data.seat_id
                and hold.status in {SeatHoldStatus.HELD, SeatHoldStatus.CONFIRMED}
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Seat is already held",
                )

        hold = await self.repository.create_seat_hold(data)
        trip = await self.repository.get_trip_by_id(data.trip_id)

        await self.event_bus.publish(
            "seat.held",
            {
                "reservation_id": str(hold.reservation_id),
                "trip_id": str(hold.trip_id),
                "seat_id": str(hold.seat_id),
            },
        )

        logger.info("seat held", extra={"reservation_id": hold.reservation_id})

        return InternalSeatHoldResponse(
            reservation_id=hold.reservation_id,
            trip_id=hold.trip_id,
            seat_id=hold.seat_id,
            status=hold.status,
            seat_gender_type=seat.gender_type,
            remaining_capacity=await self.repository.count_remaining_capacity(trip),
        )

    async def update_seat_hold_status(
        self,
        reservation_id: UUID,
        hold_status: SeatHoldStatus,
    ) -> InternalSeatHoldResponse:
        hold = await self.repository.get_seat_hold_by_reservation_id(
            reservation_id
        )

        if not hold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat hold not found",
            )

        hold = await self.repository.update_seat_hold_status(
            hold,
            hold_status,
        )
        trip = await self.repository.get_trip_by_id(hold.trip_id)
        seat = await self.repository.get_seat_by_id(hold.seat_id)

        await self.event_bus.publish(
            f"seat_hold.{hold.status.value}",
            {
                "reservation_id": str(hold.reservation_id),
                "trip_id": str(hold.trip_id),
                "seat_id": str(hold.seat_id),
                "status": hold.status.value,
            },
        )

        logger.info(
            "seat hold status changed",
            extra={
                "reservation_id": hold.reservation_id,
                "status": hold.status.value,
            },
        )

        return InternalSeatHoldResponse(
            reservation_id=hold.reservation_id,
            trip_id=hold.trip_id,
            seat_id=hold.seat_id,
            status=hold.status,
            seat_gender_type=seat.gender_type,
            remaining_capacity=await self.repository.count_remaining_capacity(trip),
        )

    @staticmethod
    def _require_transport_owner(current_user: CurrentUser) -> None:
        if current_user.role != UserRole.TRANSPORT_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only transport owners can manage transport resources",
            )
