from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import SeatGenderType, SeatHoldStatus, UserRole


class CompanyCreateRequest(BaseModel):
    name: str


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class BusCreateRequest(BaseModel):
    plate_number: str
    capacity: int
    company_id: UUID


class SeatResponse(BaseModel):
    id: UUID
    seat_number: int
    is_reservable: bool
    gender_type: SeatGenderType

    model_config = {
        "from_attributes": True
    }


class BusResponse(BaseModel):
    id: UUID
    plate_number: str
    capacity: int
    company_id: UUID
    seats: list[SeatResponse]

    model_config = {
        "from_attributes": True
    }


class TripCreateRequest(BaseModel):
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    bus_id: UUID


class TripResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    bus_id: UUID
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class CurrentUser(BaseModel):
    user_id: UUID
    role: UserRole
    gender: SeatGenderType | None = None


class SeatUpdateRequest(BaseModel):
    is_reservable: bool | None = None
    gender_type: SeatGenderType | None = None


class TripSeatResponse(BaseModel):
    seat_id: UUID
    seat_number: int
    is_reserved: bool

    model_config = {
        "from_attributes": True
    }


class InternalTripResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    bus_id: UUID
    company_name: str
    remaining_capacity: int


class InternalSeatHoldRequest(BaseModel):
    reservation_id: UUID
    passenger_gender: SeatGenderType
    trip_id: UUID
    seat_id: UUID


class InternalSeatHoldResponse(BaseModel):
    reservation_id: UUID
    trip_id: UUID
    seat_id: UUID
    status: SeatHoldStatus
    seat_gender_type: SeatGenderType
    remaining_capacity: int

    model_config = {
        "from_attributes": True
    }


class InternalSeatHoldUpdateRequest(BaseModel):
    status: SeatHoldStatus
