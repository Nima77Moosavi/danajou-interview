from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_search_service
from app.domain.schemas import TripSearchResponse
from app.domain.services import SearchService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/trips", response_model=list[TripSearchResponse])
async def search_trips(
    origin: str | None = Query(default=None),
    destination: str | None = Query(default=None),
    departure_date: date | None = Query(default=None),
    service: SearchService = Depends(get_search_service),
):
    return await service.search_trips(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
    )
