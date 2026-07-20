"""Add learning_preferences to assessments

Revision ID: 002
Revises: 001
Create Date: 2026-07-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assessments",
        sa.Column("learning_preferences", JSONB(), server_default="[]", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("assessments", "learning_preferences")
