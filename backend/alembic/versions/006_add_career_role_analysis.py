"""Add career_role_analyses table

Revision ID: 006
Revises: 005
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "career_role_analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("role_id", sa.String(100), nullable=False),
        sa.Column("role_name", sa.String(100), nullable=False),
        sa.Column("readiness_score", sa.Integer(), server_default="0"),
        sa.Column("readiness_level", sa.String(20), server_default="not_started"),
        sa.Column("total_skills", sa.Integer(), server_default="0"),
        sa.Column("covered_count", sa.Integer(), server_default="0"),
        sa.Column("partial_count", sa.Integer(), server_default="0"),
        sa.Column("missing_count", sa.Integer(), server_default="0"),
        sa.Column("skill_gaps", JSONB(), server_default="[]"),
        sa.Column("priority_breakdown", JSONB(), server_default="{}"),
        sa.Column("recommended_next_skill", JSONB(), nullable=True),
        sa.Column("learning_path", JSONB(), server_default="[]"),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("career_role_analyses")
