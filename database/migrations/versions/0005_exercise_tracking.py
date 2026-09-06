"""Add exercise tracking.

Revision ID: 0005_exercise_tracking
Revises: 0004_food_tracking
Create Date: 2026-09-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0005_exercise_tracking"
down_revision: str | Sequence[str] | None = "0004_food_tracking"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("exercise_sessions", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("activity_type", sa.Enum("walking", "running", "cycling", "strength_training", "swimming", "sports", "other", name="activity_type", native_enum=False, create_constraint=True), nullable=False), sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("duration_minutes", sa.Integer(), nullable=False), sa.Column("distance_km", sa.Numeric(precision=10, scale=3), nullable=True), sa.Column("calories_burned_kcal", sa.Numeric(precision=10, scale=3), nullable=True), sa.Column("note", sa.String(length=500), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.CheckConstraint("duration_minutes > 0", name="ck_exercise_sessions_duration_positive"), sa.CheckConstraint("distance_km IS NULL OR distance_km > 0", name="ck_exercise_sessions_distance_positive"), sa.CheckConstraint("calories_burned_kcal IS NULL OR calories_burned_kcal >= 0", name="ck_exercise_sessions_calories_non_negative"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_exercise_sessions_user_performed_at", "exercise_sessions", ["user_id", "performed_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_exercise_sessions_user_performed_at", table_name="exercise_sessions")
    op.drop_table("exercise_sessions")
