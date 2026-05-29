import logging

from fastapi import HTTPException, status

from app.domain.schemas import OTPVerifyRequest
from app.infrastructure.messaging import RabbitMQEventBus
from app.infrastructure.repositories import OTPRepository


logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        repository: OTPRepository,
        event_bus: RabbitMQEventBus | None = None,
    ):
        self.repository = repository
        self.event_bus = event_bus or RabbitMQEventBus()

    async def verify_otp(
        self,
        data: OTPVerifyRequest,
    ) -> bool:
        otp = await self.repository.get_valid_code(
            data.phone_number,
            data.code,
        )

        if not otp:
            await self.event_bus.publish(
                "otp.rejected",
                {"phone_number": data.phone_number},
            )
            logger.info("otp rejected", extra={"phone_number": data.phone_number})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP",
            )

        await self.repository.mark_consumed(otp)
        await self.event_bus.publish(
            "otp.verified",
            {"phone_number": data.phone_number},
        )
        logger.info("otp verified", extra={"phone_number": data.phone_number})

        return True

    async def get_latest_code(
        self,
        phone_number: str,
    ):
        otp = await self.repository.get_latest_code(phone_number)

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OTP not found",
            )

        return otp
