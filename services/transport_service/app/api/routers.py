from fastapi import (
    APIRouter,
    Depends,
)

from app.api.deps import (
    get_transport_service,
)

from app.domain.services import (
    TransportService,
)

from app.domain.schemas import (
    BusCreateRequest,
    BusResponse,
    TripCreateRequest,
    TripResponse,
)


router = APIRouter(
    prefix="/transport",
    tags=["Transport"],
)


@router.post(
    "/buses",
    response_model=BusResponse,
)
async def create_bus(
    data: BusCreateRequest,
    service: TransportService = Depends(
        get_transport_service
    ),
):
    return await service.create_bus(data)


@router.post(
    "/trips",
    response_model=TripResponse,
)
async def create_trip(
    data: TripCreateRequest,
    service: TransportService = Depends(
        get_transport_service
    ),
):
    return await service.create_trip(data)


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