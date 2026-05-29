from typing import Protocol
from uuid import UUID

from app.infrastructure.models import User
from app.domain.enums import UserGender, UserRole


class IUserRepository(Protocol):
    async def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        ...

    async def get_user_by_phone_number(self, phone_number: str) -> User | None:
        ...

    async def create_user(
        self, phone_number: str,
        password_hash: str | None,
        gender: UserGender,
        role: UserRole,
        is_active: bool = True
    ) -> User:
        ...
