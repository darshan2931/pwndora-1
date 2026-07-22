"""Add mentor_memories table for Phase 7 enhanced mentor context

Revision ID: 009
Revises: 008
Create Date: 2026-07-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mentor_memories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("important_facts", JSONB(), server_default="[]"),
        sa.Column("current_goals", JSONB(), server_default="[]"),
        sa.Column("blockers", JSONB(), server_default="[]"),
        sa.Column("next_actions", JSONB(), server_default="[]"),
        sa.Column("learning_preferences", JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_mentor_memories_user_id", "mentor_memories", ["user_id"])
    op.create_index("ix_mentor_memories_session_id", "mentor_memories", ["session_id"])
    op.create_index(
        "ix_mentor_memories_user_id_session_id",
        "mentor_memories",
        ["user_id", "session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_mentor_memories_user_id_session_id", table_name="mentor_memories")
    op.drop_index("ix_mentor_memories_session_id", table_name="mentor_memories")
    op.drop_index("ix_mentor_memories_user_id", table_name="mentor_memories")
    op.drop_table("mentor_memories")
