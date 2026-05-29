"""create reservations table

Revision ID: 1f3a2b4c5d6e
Revises:
Create Date: 2026-05-29 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1f3a2b4c5d6e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("passenger_id", sa.UUID(), nullable=False),
        sa.Column("passenger_gender", sa.String(length=10), nullable=False),
        sa.Column("trip_id", sa.UUID(), nullable=False),
        sa.Column("seat_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "CONFIRMED",
                "CANCELLED",
                "EXPIRED",
                name="reservationstatus",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reservations_passenger_id"),
        "reservations",
        ["passenger_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reservations_passenger_id"), table_name="reservations")
    op.drop_table("reservations")
