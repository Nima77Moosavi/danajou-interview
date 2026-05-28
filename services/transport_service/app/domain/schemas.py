from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class BusCreateRequest(BaseModel):
    plate_number: str
    capacity: int
    operator_name: str


class BusResponse(BaseModel):
    id: UUID
    plate_number: str
    capacity: int
    operator_name: str

    model_config = {
        "from_attributes": True
    }


class TripCreateRequest(BaseModel):
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    available_seats: int
    bus_id: UUID


class TripResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    available_seats: int
    bus_id: UUID

    model_config = {
        "from_attributes": True
    }