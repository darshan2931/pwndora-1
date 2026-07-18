"""Add user_id to chat_history

Revision ID: 002
Revises: 001
Create Date: 2025-02-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_history",
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, server_default=sa.text("'00000000-0000-0000-0000-000000000000'::uuid")),
    )
    op.create_index("ix_chat_history_user_id", "chat_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_history_user_id", table_name="chat_history")
    op.drop_column("chat_history", "user_id")
