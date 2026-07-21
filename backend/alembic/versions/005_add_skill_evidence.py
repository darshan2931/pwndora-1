"""Add skill_evidence and user_skill_profiles tables

Revision ID: 005
Revises: 004
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skill_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("skill_id", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("confidence", sa.Integer(), server_default="0"),
        sa.Column("confidence_level", sa.String(20), server_default="minimal"),
        sa.Column("sources", JSONB(), server_default="[]"),
        sa.Column("evidence_count", sa.Integer(), server_default="0"),
        sa.Column("strongest_source", sa.String(50), nullable=True),
        sa.Column("last_updated", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "user_skill_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("total_skills", sa.Integer(), server_default="0"),
        sa.Column("high_confidence_count", sa.Integer(), server_default="0"),
        sa.Column("medium_confidence_count", sa.Integer(), server_default="0"),
        sa.Column("low_confidence_count", sa.Integer(), server_default="0"),
        sa.Column("minimal_confidence_count", sa.Integer(), server_default="0"),
        sa.Column("average_confidence", sa.Integer(), server_default="0"),
        sa.Column("analysis_status", sa.String(20), server_default="pending"),
        sa.Column("analysis_error", sa.Text(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("user_skill_profiles")
    op.drop_table("skill_evidence")
