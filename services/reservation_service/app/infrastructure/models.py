import uuid
from datetime import datetime

from sqlalchemy import (
    Enum,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database import Base

from app.domain.enums import ReservationStatus


class Reservation(Base):
    __tablename__ = "reservations"

    __table_args__ = (
        UniqueConstraint(
            "trip_id",
            "seat_id",
            name="uq_trip_seat",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passenger_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True,)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    seat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    status: Mapped[ReservationStatus] = mapped_column(
        Enum(
            ReservationStatus,
            native_enum=False,
            length=20,
        ),
        default=ReservationStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(),)
