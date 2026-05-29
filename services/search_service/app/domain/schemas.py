from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TripSearchResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    bus_id: UUID
    company_name: str
    remaining_capacity: int
