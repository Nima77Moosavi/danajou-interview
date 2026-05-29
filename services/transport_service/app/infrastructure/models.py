import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    func,
    Enum,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database import Base

from app.domain.enums import (
    SeatGenderType,
    ReservationStatus,
)


class TransportCompany(Base):
    __tablename__ = "transport_companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    buses: Mapped[list["Bus"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


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

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transport_companies.id"),
        nullable=False,
    )

    company: Mapped["TransportCompany"] = relationship(
        back_populates="buses",
    )

    seats: Mapped[list["Seat"]] = relationship(
        back_populates="bus",
        cascade="all, delete-orphan",
    )

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="bus",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


class Seat(Base):
    __tablename__ = "seats"

    __table_args__ = (
        UniqueConstraint(
            "bus_id",
            "seat_number",
            name="uq_bus_seat_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    seat_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_reservable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    gender_type: Mapped[SeatGenderType] = mapped_column(
        Enum(
            SeatGenderType,
            native_enum=False,
            length=20,
        ),
        nullable=False,
    )

    bus_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buses.id"),
        nullable=False,
    )

    bus: Mapped["Bus"] = relationship(
        back_populates="seats",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="seat",
        cascade="all, delete-orphan",
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
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    departure_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    arrival_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    bus_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("buses.id"),
        nullable=False,
    )

    bus: Mapped["Bus"] = relationship(
        back_populates="trips",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


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
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    passenger_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trips.id"),
        nullable=False,
    )

    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("seats.id"),
        nullable=False,
    )

    status: Mapped[ReservationStatus] = mapped_column(
        Enum(
            ReservationStatus,
            native_enum=False,
            length=20,
        ),
        default=ReservationStatus.RESERVED,
        nullable=False,
    )

    reserved_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="reservations",
    )

    seat: Mapped["Seat"] = relationship(
        back_populates="reservations",
    )
