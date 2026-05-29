"""create otp codes table

Revision ID: 3f4a5b6c7d8e
Revises:
Create Date: 2026-05-29 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3f4a5b6c7d8e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "otp_codes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_consumed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_otp_codes_phone_number"),
        "otp_codes",
        ["phone_number"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_otp_codes_phone_number"), table_name="otp_codes")
    op.drop_table("otp_codes")
