"""Add roadmap versioning fields

Revision ID: 007
Revises: 006
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("roadmaps", sa.Column("user_id", sa.String(36), nullable=True))
    op.add_column("roadmaps", sa.Column("version", sa.Integer(), server_default="1"))
    op.add_column("roadmaps", sa.Column("generation_reason", sa.String(100), nullable=True))
    op.add_column("roadmaps", sa.Column("readiness_score_at_creation", sa.Integer(), server_default="0"))
    op.add_column("roadmaps", sa.Column("phases", JSONB(), server_default="[]"))
    op.create_index("ix_roadmaps_user_id", "roadmaps", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_roadmaps_user_id", "roadmaps")
    op.drop_column("roadmaps", "phases")
    op.drop_column("roadmaps", "readiness_score_at_creation")
    op.drop_column("roadmaps", "generation_reason")
    op.drop_column("roadmaps", "version")
    op.drop_column("roadmaps", "user_id")
