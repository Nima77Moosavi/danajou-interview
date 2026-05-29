from pathlib import Path
from typing import AsyncGenerator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@auth_db:5432/auth_db"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    NOTIFICATION_SERVICE_URL: str = "http://notification_service:8000"
    NOTIFICATION_SERVICE_USERNAME: str = "auth_service"
    NOTIFICATION_SERVICE_PASSWORD: str = "auth-secret"

    SERVICE_CREDENTIALS: str = (
        "transport_service:transport-secret,"
        "reservation_service:reservation-secret,"
        "search_service:search-secret,"
        "notification_service:notification-secret"
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )


settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
