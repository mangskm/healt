"""Add goals.

Revision ID: 0003_goals
Revises: 0002_weight_records
Create Date: 2026-09-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0003_goals"
down_revision: str | Sequence[str] | None = "0002_weight_records"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("goal_type", sa.Enum("target_weight", name="goal_type", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("target_value_kg", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Enum("active", "completed", "cancelled", name="goal_status", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("target_value_kg > 0", name="ck_goals_target_value_kg_positive"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_goals_user_status", "goals", ["user_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_goals_user_status", table_name="goals")
    op.drop_table("goals")
