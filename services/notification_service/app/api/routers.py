from fastapi import APIRouter, Depends

from app.api.deps import get_notification_service, require_service_auth
from app.domain.schemas import DevOTPResponse, OTPVerifyRequest, OTPVerifyResponse
from app.domain.services import NotificationService


router = APIRouter(tags=["Notifications"])


@router.post(
    "/internal/otp/verify",
    response_model=OTPVerifyResponse,
    dependencies=[Depends(require_service_auth)],
)
async def verify_otp(
    data: OTPVerifyRequest,
    service: NotificationService = Depends(get_notification_service),
):
    verified = await service.verify_otp(data)

    return OTPVerifyResponse(verified=verified)


@router.get(
    "/notifications/dev/otp/{phone_number}",
    response_model=DevOTPResponse,
)
async def latest_dev_otp(
    phone_number: str,
    service: NotificationService = Depends(get_notification_service),
):
    otp = await service.get_latest_code(phone_number)

    return DevOTPResponse(
        phone_number=otp.phone_number,
        code=otp.code,
        expires_at=otp.expires_at,
        is_consumed=otp.is_consumed,
    )
