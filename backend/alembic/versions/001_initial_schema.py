"""Complete initial schema - all 15 tables

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 2. cyber_profiles
    op.create_table(
        "cyber_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("career_goal", sa.String(100), nullable=False),
        sa.Column("readiness_score", sa.Integer, server_default="0"),
        sa.Column("known_skills", JSONB, server_default="[]"),
        sa.Column("missing_skills", JSONB, server_default="[]"),
        sa.Column("completed_skills", JSONB, server_default="[]"),
        sa.Column("projects", JSONB, server_default="[]"),
        sa.Column("certifications", JSONB, server_default="[]"),
        sa.Column("achievements", JSONB, server_default="[]"),
        sa.Column("learning_preference", sa.String(50), server_default="'hands-on'"),
        sa.Column("weekly_hours", sa.Integer, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 3. assessments
    op.create_table(
        "assessments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("career_goal", sa.String(100), nullable=False),
        sa.Column("readiness_score", sa.Integer, server_default="0"),
        sa.Column("matched_skills", JSONB, server_default="[]"),
        sa.Column("missing_skills", JSONB, server_default="[]"),
        sa.Column("weekly_hours", sa.Integer, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 4. roadmaps
    op.create_table(
        "roadmaps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assessment_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("steps", JSONB, server_default="[]"),
        sa.Column("total_hours", sa.Integer, server_default="0"),
        sa.Column("estimated_weeks", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 5. chat_memory
    op.create_table(
        "chat_memory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("session_id", sa.String(100), nullable=False, index=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("important_facts", JSONB, server_default="[]"),
        sa.Column("next_goal", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 6. resume_analysis
    op.create_table(
        "resume_analysis",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("file_path", sa.String(255), nullable=False),
        sa.Column("career_goal", sa.String(100), nullable=False),
        sa.Column("extracted_data", JSONB, server_default="{}"),
        sa.Column("feedback", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 7. chat_history
    op.create_table(
        "chat_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("assessment_id", UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=False, index=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 8. resume_reviews
    op.create_table(
        "resume_reviews",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("career_goal", sa.String(100), nullable=False),
        sa.Column("feedback", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 9. skills
    op.create_table(
        "skills",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), server_default="'learning'"),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 10. projects
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), server_default="'in-progress'"),
        sa.Column("github_link", sa.String(255)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 11. missions
    op.create_table(
        "missions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(50), server_default="'pending'"),
        sa.Column("reward_points", sa.Integer, server_default="50"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 12. progress
    op.create_table(
        "progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("study_hours", sa.Integer, server_default="0"),
        sa.Column("quizzes_taken", sa.Integer, server_default="0"),
        sa.Column("streak_days", sa.Integer, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 13. weekly_reports
    op.create_table(
        "weekly_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("week_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("achievements", JSONB, server_default="[]"),
        sa.Column("next_focus", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 14. achievements
    op.create_table(
        "achievements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("icon", sa.String(50)),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 15. knowledge_cache
    op.create_table(
        "knowledge_cache",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("cache_key", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("data", JSONB, nullable=False),
        sa.Column("prompt_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("knowledge_cache")
    op.drop_table("achievements")
    op.drop_table("weekly_reports")
    op.drop_table("progress")
    op.drop_table("missions")
    op.drop_table("projects")
    op.drop_table("skills")
    op.drop_table("resume_reviews")
    op.drop_table("chat_history")
    op.drop_table("resume_analysis")
    op.drop_table("chat_memory")
    op.drop_table("roadmaps")
    op.drop_table("assessments")
    op.drop_table("cyber_profiles")
    op.drop_table("users")
