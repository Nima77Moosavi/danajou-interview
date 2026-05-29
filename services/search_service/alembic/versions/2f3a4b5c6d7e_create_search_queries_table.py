"""create search queries table

Revision ID: 2f3a4b5c6d7e
Revises:
Create Date: 2026-05-29 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f3a4b5c6d7e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "search_queries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("origin", sa.String(length=100), nullable=True),
        sa.Column("destination", sa.String(length=100), nullable=True),
        sa.Column("departure_date", sa.Date(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("search_queries")
