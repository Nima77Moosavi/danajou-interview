"""create transport tables

Revision ID: 4eb58d493eba
Revises:
Create Date: 2026-05-28 11:40:57.037533
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4eb58d493eba"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transport_companies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_transport_companies_owner_id"),
        "transport_companies",
        ["owner_id"],
        unique=False,
    )

    op.create_table(
        "buses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("plate_number", sa.String(length=50), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["company_id"], ["transport_companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plate_number"),
    )

    op.create_table(
        "seats",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("seat_number", sa.Integer(), nullable=False),
        sa.Column("is_reservable", sa.Boolean(), nullable=False),
        sa.Column(
            "gender_type",
            sa.Enum(
                "NONE",
                "MALE",
                "FEMALE",
                name="seatgendertype",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("bus_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["bus_id"], ["buses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bus_id", "seat_number", name="uq_bus_seat_number"),
    )

    op.create_table(
        "trips",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("origin", sa.String(length=100), nullable=False),
        sa.Column("destination", sa.String(length=100), nullable=False),
        sa.Column("departure_time", sa.DateTime(), nullable=False),
        sa.Column("arrival_time", sa.DateTime(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("bus_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["bus_id"], ["buses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trips_destination"), "trips", ["destination"])
    op.create_index(op.f("ix_trips_origin"), "trips", ["origin"])

    op.create_table(
        "seat_holds",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("reservation_id", sa.UUID(), nullable=False),
        sa.Column("trip_id", sa.UUID(), nullable=False),
        sa.Column("seat_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "HELD",
                "CONFIRMED",
                "RELEASED",
                name="seatholdstatus",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["seat_id"], ["seats.id"]),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_seat_holds_reservation_id"),
        "seat_holds",
        ["reservation_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_seat_holds_reservation_id"), table_name="seat_holds")
    op.drop_table("seat_holds")
    op.drop_index(op.f("ix_trips_origin"), table_name="trips")
    op.drop_index(op.f("ix_trips_destination"), table_name="trips")
    op.drop_table("trips")
    op.drop_table("seats")
    op.drop_table("buses")
    op.drop_index(
        op.f("ix_transport_companies_owner_id"),
        table_name="transport_companies",
    )
    op.drop_table("transport_companies")
