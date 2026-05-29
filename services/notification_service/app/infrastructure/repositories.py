from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import settings
from app.infrastructure.models import OTPCode


class OTPRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_code(
        self,
        phone_number: str,
        code: str,
    ) -> OTPCode:
        otp = OTPCode(
            phone_number=phone_number,
            code=code,
            expires_at=datetime.now(UTC).replace(tzinfo=None)
            + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )

        self.session.add(otp)
        await self.session.commit()
        await self.session.refresh(otp)

        return otp

    async def get_valid_code(
        self,
        phone_number: str,
        code: str,
    ) -> OTPCode | None:
        stmt = (
            select(OTPCode)
            .where(
                OTPCode.phone_number == phone_number,
                OTPCode.code == code,
                OTPCode.is_consumed.is_(False),
                OTPCode.expires_at > datetime.now(UTC).replace(tzinfo=None),
            )
            .order_by(desc(OTPCode.created_at))
        )
        result = await self.session.execute(stmt)

        return result.scalars().first()

    async def mark_consumed(
        self,
        otp: OTPCode,
    ) -> OTPCode:
        otp.is_consumed = True
        otp.verified_at = datetime.now(UTC).replace(tzinfo=None)

        await self.session.commit()
        await self.session.refresh(otp)

        return otp

    async def get_latest_code(
        self,
        phone_number: str,
    ) -> OTPCode | None:
        stmt = (
            select(OTPCode)
            .where(OTPCode.phone_number == phone_number)
            .order_by(desc(OTPCode.created_at))
        )
        result = await self.session.execute(stmt)

        return result.scalars().first()
