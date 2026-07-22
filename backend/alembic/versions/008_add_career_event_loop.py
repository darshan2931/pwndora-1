"""Add career evidence event loop and roadmap versioning tables

Revision ID: 008
Revises: 007
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # CareerEvidenceEvent
    op.create_table(
        "career_evidence_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_data", JSONB(), server_default="{}"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_career_evidence_events_user_id", "career_evidence_events", ["user_id"])
    op.create_index("ix_career_evidence_events_idempotency_key", "career_evidence_events", ["idempotency_key"])
    op.create_index("ix_career_evidence_events_user_id_created_at", "career_evidence_events", ["user_id", "created_at"])

    # CareerChangeLog
    op.create_table(
        "career_change_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("event_id", sa.String(36), nullable=False),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=True),
        sa.Column("old_value", JSONB(), nullable=True),
        sa.Column("new_value", JSONB(), nullable=True),
        sa.Column("confidence_delta", sa.Integer(), server_default="0"),
        sa.Column("readiness_delta", sa.Integer(), server_default="0"),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_career_change_logs_user_id", "career_change_logs", ["user_id"])
    op.create_index("ix_career_change_logs_event_id", "career_change_logs", ["event_id"])
    op.create_index("ix_career_change_logs_user_id_created_at", "career_change_logs", ["user_id", "created_at"])

    # RoadmapVersion
    op.create_table(
        "roadmap_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("assessment_id", sa.String(36), nullable=False),
        sa.Column("version_number", sa.Integer(), server_default="1"),
        sa.Column("generation_reason", sa.String(100), nullable=True),
        sa.Column("triggered_by_event_id", sa.String(36), nullable=True),
        sa.Column("previous_version_id", sa.String(36), nullable=True),
        sa.Column("readiness_score_at_creation", sa.Integer(), server_default="0"),
        sa.Column("nodes_snapshot", JSONB(), server_default="[]"),
        sa.Column("phases_snapshot", JSONB(), server_default="[]"),
        sa.Column("total_hours", sa.Integer(), server_default="0"),
        sa.Column("estimated_weeks", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_roadmap_versions_user_id", "roadmap_versions", ["user_id"])
    op.create_index("ix_roadmap_versions_assessment_id", "roadmap_versions", ["assessment_id"])
    op.create_index("ix_roadmap_versions_user_id_version", "roadmap_versions", ["user_id", "version_number"])


def downgrade() -> None:
    op.drop_index("ix_roadmap_versions_user_id_version", "roadmap_versions")
    op.drop_index("ix_roadmap_versions_assessment_id", "roadmap_versions")
    op.drop_index("ix_roadmap_versions_user_id", "roadmap_versions")
    op.drop_table("roadmap_versions")

    op.drop_index("ix_career_change_logs_user_id_created_at", "career_change_logs")
    op.drop_index("ix_career_change_logs_event_id", "career_change_logs")
    op.drop_index("ix_career_change_logs_user_id", "career_change_logs")
    op.drop_table("career_change_logs")

    op.drop_index("ix_career_evidence_events_user_id_created_at", "career_evidence_events")
    op.drop_index("ix_career_evidence_events_idempotency_key", "career_evidence_events")
    op.drop_index("ix_career_evidence_events_user_id", "career_evidence_events")
    op.drop_table("career_evidence_events")
