from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_user,
    get_transport_service,
    require_service_auth,
)
from app.domain.schemas import (
    BusCreateRequest,
    BusResponse,
    CompanyCreateRequest,
    CompanyResponse,
    CurrentUser,
    InternalSeatHoldRequest,
    InternalSeatHoldResponse,
    InternalSeatHoldUpdateRequest,
    InternalTripResponse,
    SeatResponse,
    SeatUpdateRequest,
    TripCreateRequest,
    TripResponse,
)
from app.domain.services import TransportService


router = APIRouter(
    prefix="/transport",
    tags=["Transport"],
)


@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=201,
)
async def create_company(
    data: CompanyCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(get_transport_service),
):
    return await service.create_company(current_user, data)


@router.post(
    "/buses",
    response_model=BusResponse,
    status_code=201,
)
async def create_bus(
    data: BusCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(get_transport_service),
):
    return await service.create_bus(current_user, data)


@router.post(
    "/trips",
    response_model=TripResponse,
    status_code=201,
)
async def create_trip(
    data: TripCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(get_transport_service),
):
    return await service.create_trip(current_user, data)


@router.get(
    "/trips",
    response_model=list[TripResponse],
)
async def list_trips(
    service: TransportService = Depends(get_transport_service),
):
    return await service.list_trips()


@router.patch(
    "/seats/{seat_id}",
    response_model=SeatResponse,
)
async def update_seat(
    seat_id: UUID,
    data: SeatUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(get_transport_service),
):
    return await service.update_seat(current_user, seat_id, data)


@router.get(
    "/internal/trips",
    response_model=list[InternalTripResponse],
    dependencies=[Depends(require_service_auth)],
)
async def search_trips(
    origin: str | None = Query(default=None),
    destination: str | None = Query(default=None),
    departure_date: date | None = Query(default=None),
    service: TransportService = Depends(get_transport_service),
):
    return await service.search_trips(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
    )


@router.post(
    "/internal/seat-holds",
    response_model=InternalSeatHoldResponse,
    dependencies=[Depends(require_service_auth)],
    status_code=201,
)
async def hold_seat(
    data: InternalSeatHoldRequest,
    service: TransportService = Depends(get_transport_service),
):
    return await service.hold_seat(data)


@router.patch(
    "/internal/seat-holds/{reservation_id}",
    response_model=InternalSeatHoldResponse,
    dependencies=[Depends(require_service_auth)],
)
async def update_seat_hold(
    reservation_id: UUID,
    data: InternalSeatHoldUpdateRequest,
    service: TransportService = Depends(get_transport_service),
):
    return await service.update_seat_hold_status(
        reservation_id=reservation_id,
        hold_status=data.status,
    )
