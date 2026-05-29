from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    PASSENGER = "passenger"
    TRANSPORT_OWNER = "transport_owner"


class SeatGenderType(StrEnum):
    MALE = "male"
    FEMALE = "female"


class ReservationStatus(StrEnum):
    RESERVED = "reserved"
    CANCELLED = "cancelled"
