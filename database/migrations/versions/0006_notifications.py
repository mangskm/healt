"""Add in-app reminders.

Revision ID: 0006_notifications
Revises: 0005_exercise_tracking
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0006_notifications"
down_revision: str | Sequence[str] | None = "0005_exercise_tracking"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reminders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("reminder_type", sa.Enum("weight", "meal", "exercise", "custom", name="reminder_type", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("reminder_time", sa.Time(), nullable=False),
        sa.Column("schedule_type", sa.Enum("daily", "weekly", name="reminder_schedule_type", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)", name="ck_reminders_day_of_week_range"),
        sa.CheckConstraint("(schedule_type = 'daily' AND day_of_week IS NULL) OR (schedule_type = 'weekly' AND day_of_week IS NOT NULL)", name="ck_reminders_schedule_day"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminders_user_enabled_time", "reminders", ["user_id", "enabled", "reminder_time"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reminders_user_enabled_time", table_name="reminders")
    op.drop_table("reminders")
