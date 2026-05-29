from fastapi import HTTPException, status

from app.domain.interfaces import (
    ITransportRepository,
)

from app.domain.schemas import (
    CurrentUser,
    CompanyCreateRequest,
    BusCreateRequest,
    TripCreateRequest,
    ReservationCreateRequest
)

from app.domain.enums import UserRole


class TransportService:
    def __init__(
        self,
        repository: ITransportRepository,
    ):
        self.repository = repository

    async def create_company(
        self,
        current_user: CurrentUser,
        data: CompanyCreateRequest,
    ):

        if current_user.role != UserRole.TRANSPORT_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only transport owners can create companies",
            )

        existing_company = await self.repository.get_company_by_owner(
            current_user.user_id
        )

        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner already has a company",
            )

        return await self.repository.create_company(
            owner_id=current_user.user_id,
            data=data,
        )

    async def create_bus(
        self,
        current_user: CurrentUser,
        data: BusCreateRequest,
    ):

        company = await self.repository.get_company_by_id(
            data.company_id
        )

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

        return await self.repository.create_bus(data)

    async def create_trip(
        self,
        current_user: CurrentUser,
        data: TripCreateRequest,
    ):

        bus = await self.repository.get_bus_by_id(
            data.bus_id
        )

        if not bus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bus not found",
            )

        company = bus.company

        if company.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this bus",
            )

        return await self.repository.create_trip(data)

    async def list_trips(
        self,
    ):
        return await self.repository.list_trips()

    async def create_reservation(
        self,
        current_user: CurrentUser,
        data: ReservationCreateRequest,
    ):
        trip = await self.repository.get_trip_by_id(
            data.trip_id
        )

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found",
            )

        seat = await self.repository.get_seat_by_id(
            data.seat_id
        )

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

        existing_reservation = await self.repository.get_reservation(
            trip_id=data.trip_id,
            seat_id=data.seat_id,
        )

        if existing_reservation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seat already reserved",
            )

        return await self.repository.create_reservation(
            passenger_id=current_user.user_id,
            data=data,
        )
