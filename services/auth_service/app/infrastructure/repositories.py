from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import UserGender, UserRole
from app.domain.interfaces import IUserRepository
from app.infrastructure.models import User


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        stmt = select(User).where(
            User.id == user_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_by_phone_number(self, phone_number: str) -> User | None:
        stmt = (
            select(User).
            where(User.phone_number == phone_number)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        phone_number: str,
        password_hash: str | None,
        gender: UserGender,
        role: UserRole,
        is_active: bool = True
    ) -> User:
        user = User(
            phone_number=phone_number,
            password_hash=password_hash,
            gender=gender,
            role=role,
            is_active=is_active
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
