import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database import Base


class Bus(Base):
    __tablename__ = "buses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    plate_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    operator_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="bus",
    )


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    origin: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    destination: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    departure_time: Mapped[datetime]

    arrival_time: Mapped[datetime]

    price: Mapped[int]

    available_seats: Mapped[int]

    bus_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buses.id"),
    )

    bus: Mapped["Bus"] = relationship(
        back_populates="trips",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )