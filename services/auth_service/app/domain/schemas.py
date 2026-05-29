from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.enums import UserRole, UserGender


class UserRegisterRequest(BaseModel):
    phone_number: str
    password: str | None = None
    gender: UserGender
    role: UserRole = UserRole.PASSENGER


class LoginRequest(BaseModel):
    phone_number: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    phone_number: str
    role: UserRole
    gender: UserGender
    created_at: datetime

    model_config = {
        'from_attributes': True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OTPRequest(BaseModel):
    phone_number: str
    gender: UserGender


class OTPVerifyRequest(BaseModel):
    phone_number: str
    code: str = Field(min_length=4, max_length=8)
    gender: UserGender


class MessageResponse(BaseModel):
    detail: str
