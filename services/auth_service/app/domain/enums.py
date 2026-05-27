from enum import StrEnum


class UserGender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class UserRole(StrEnum):
    ADMIN = "admin"
    PASSENGER = "passenger"
    TRANSPORT_OWNER = "transport_owner"
