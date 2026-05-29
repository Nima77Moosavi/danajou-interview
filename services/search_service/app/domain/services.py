import logging
from datetime import date

import httpx
from fastapi import HTTPException, status

from app.domain.schemas import TripSearchResponse
from app.infrastructure.database import settings
from app.infrastructure.repositories import SearchRepository


logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, repository: SearchRepository):
        self.repository = repository

    async def search_trips(
        self,
        origin: str | None,
        destination: str | None,
        departure_date: date | None,
    ) -> list[TripSearchResponse]:
        params = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date.isoformat()
            if departure_date
            else None,
        }
        params = {key: value for key, value in params.items() if value is not None}

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{settings.TRANSPORT_SERVICE_URL}/transport/internal/trips",
                    auth=(
                        settings.TRANSPORT_SERVICE_USERNAME,
                        settings.TRANSPORT_SERVICE_PASSWORD,
                    ),
                    params=params,
                )
            except httpx.HTTPError as exc:
                logger.exception("transport search request failed")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Transport service is unavailable",
                ) from exc

        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text,
            )

        trips = [TripSearchResponse(**item) for item in response.json()]

        await self.repository.log_search(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            result_count=len(trips),
        )

        return trips
