"""Add github_profiles and github_repository_evidence tables

Revision ID: 004
Revises: 003
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "github_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("resume_profile_id", sa.String(36), nullable=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("profile_url", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("public_repositories", sa.Integer(), server_default="0"),
        sa.Column("followers", sa.Integer(), server_default="0"),
        sa.Column("following", sa.Integer(), server_default="0"),
        sa.Column("account_created_at", sa.String(50), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_status", sa.String(20), server_default="pending"),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "github_repository_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("github_profile_id", sa.String(36), nullable=False, index=True),
        sa.Column("repository_name", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("repository_url", sa.String(500), nullable=False),
        sa.Column("languages", JSONB(), server_default="{}"),
        sa.Column("topics", JSONB(), server_default="[]"),
        sa.Column("dependencies", JSONB(), server_default="[]"),
        sa.Column("readme_text", sa.Text(), nullable=True),
        sa.Column("readme_available", sa.Integer(), server_default="0"),
        sa.Column("stars", sa.Integer(), server_default="0"),
        sa.Column("forks", sa.Integer(), server_default="0"),
        sa.Column("is_fork", sa.Integer(), server_default="0"),
        sa.Column("is_archived", sa.Integer(), server_default="0"),
        sa.Column("created_at_github", sa.String(50), nullable=True),
        sa.Column("updated_at_github", sa.String(50), nullable=True),
        sa.Column("pushed_at_github", sa.String(50), nullable=True),
        sa.Column("selection_reasons", JSONB(), server_default="[]"),
        sa.Column("ai_analysis", JSONB(), server_default="{}"),
        sa.Column("tech_evidence", JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("github_repository_evidence")
    op.drop_table("github_profiles")
