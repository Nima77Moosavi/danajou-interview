from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    PASSENGER = "passenger"
    TRANSPORT_OWNER = "transport_owner"


class SeatGenderType(StrEnum):
    NONE = "none"
    MALE = "male"
    FEMALE = "female"


class ReservationStatus(StrEnum):
    RESERVED = "reserved"
    CANCELLED = "cancelled"


class SeatHoldStatus(StrEnum):
    HELD = "held"
    CONFIRMED = "confirmed"
    RELEASED = "released"
