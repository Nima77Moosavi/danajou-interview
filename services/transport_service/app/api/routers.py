from fastapi import (
    APIRouter,
    Depends,
)

from app.api.deps import (
    get_transport_service,
    get_current_user,
)

from app.domain.services import (
    TransportService,
)

from app.domain.schemas import (
    CurrentUser,
    CompanyCreateRequest,
    CompanyResponse,
    BusCreateRequest,
    BusResponse,
    TripCreateRequest,
    TripResponse,
    ReservationCreateRequest,
    ReservationResponse
)


router = APIRouter(
    prefix="/transport",
    tags=["Transport"],
)


@router.post(
    "/companies",
    response_model=CompanyResponse,
)
async def create_company(
    data: CompanyCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(
        get_transport_service
    ),
):
    return await service.create_company(
        current_user,
        data,
    )


@router.post(
    "/buses",
    response_model=BusResponse,
)
async def create_bus(
    data: BusCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(
        get_transport_service
    ),
):
    return await service.create_bus(
        current_user,
        data,
    )


@router.post(
    "/trips",
    response_model=TripResponse,
)
async def create_trip(
    data: TripCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(
        get_transport_service
    ),
):
    return await service.create_trip(
        current_user,
        data,
    )


@router.get(
    "/trips",
    response_model=list[TripResponse],
)
async def list_trips(
    service: TransportService = Depends(
        get_transport_service
    ),
):
    return await service.list_trips()


@router.post("/reservations")
async def create_reservation(
    data: ReservationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: TransportService = Depends(get_transport_service)
) -> ReservationResponse:
    return await service.create_reservation(
        current_user=current_user,
        data=data,
    )
