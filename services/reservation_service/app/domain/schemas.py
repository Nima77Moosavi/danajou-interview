from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.domain.enums import ReservationStatus


class CurrentUser(BaseModel):
    user_id: UUID
    role: str


class ReservationCreateRequest(BaseModel):
    trip_id: UUID
    seat_id: UUID


class ReservationResponse(BaseModel):
    passenger_id: UUID
    trip_id: UUID
    seat_id: UUID
    status: ReservationStatus
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
