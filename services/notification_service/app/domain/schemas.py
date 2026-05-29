from datetime import datetime

from pydantic import BaseModel, Field


class OTPVerifyRequest(BaseModel):
    phone_number: str
    code: str = Field(min_length=4, max_length=8)


class OTPVerifyResponse(BaseModel):
    verified: bool


class DevOTPResponse(BaseModel):
    phone_number: str
    code: str
    expires_at: datetime
    is_consumed: bool
