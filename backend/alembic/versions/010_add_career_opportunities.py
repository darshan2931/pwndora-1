"""Add career opportunity intelligence tables

Revision ID: 010
Revises: 009
Create Date: 2026-07-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "career_opportunities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("organization", sa.String(255), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("remote", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("opportunity_type", sa.String(50), nullable=True),
        sa.Column("experience_level", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "opportunity_requirements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("requirement_type", sa.String(20), nullable=False),
        sa.Column("importance", sa.String(20), server_default="important"),
        sa.Column("importance_score", sa.Integer(), server_default="50"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_opportunity_requirements_opportunity_id", "opportunity_requirements", ["opportunity_id"])

    op.create_table(
        "opportunity_matches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("opportunity_id", sa.String(36), nullable=False),
        sa.Column("match_score", sa.Integer(), server_default="0"),
        sa.Column("required_skill_coverage", sa.Integer(), server_default="0"),
        sa.Column("preferred_skill_coverage", sa.Integer(), server_default="0"),
        sa.Column("evidence_score", sa.Integer(), server_default="0"),
        sa.Column("certification_score", sa.Integer(), server_default="0"),
        sa.Column("missing_skills", JSONB(), server_default="[]"),
        sa.Column("strengths", JSONB(), server_default="[]"),
        sa.Column("match_category", sa.String(30), server_default="early_gap"),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("prepared_plan", JSONB(), server_default="{}"),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_opportunity_matches_user_id", "opportunity_matches", ["user_id"])
    op.create_index("ix_opportunity_matches_opportunity_id", "opportunity_matches", ["opportunity_id"])
    op.create_index(
        "ix_opportunity_matches_user_opportunity",
        "opportunity_matches",
        ["user_id", "opportunity_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_opportunity_matches_user_opportunity", table_name="opportunity_matches")
    op.drop_index("ix_opportunity_matches_opportunity_id", table_name="opportunity_matches")
    op.drop_index("ix_opportunity_matches_user_id", table_name="opportunity_matches")
    op.drop_table("opportunity_matches")
    op.drop_index("ix_opportunity_requirements_opportunity_id", table_name="opportunity_requirements")
    op.drop_table("opportunity_requirements")
    op.drop_table("career_opportunities")
