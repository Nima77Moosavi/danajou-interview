from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.domain.enums import UserRole, UserGender


class UserRegisterRequest(BaseModel):
    phone_number: str
    password: str
    gender: UserGender


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
