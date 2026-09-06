"""Add food and meal tracking.

Revision ID: 0004_food_tracking
Revises: 0003_goals
Create Date: 2026-09-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_food_tracking"
down_revision: str | Sequence[str] | None = "0003_goals"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("meals", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("meal_type", sa.Enum("breakfast", "lunch", "dinner", "snack", "other", name="meal_type", native_enum=False, create_constraint=True), nullable=False), sa.Column("eaten_at", sa.DateTime(timezone=True), nullable=False), sa.Column("note", sa.String(length=500), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_meals_user_eaten_at", "meals", ["user_id", "eaten_at"], unique=False)
    op.create_table("meal_items", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("meal_id", sa.Uuid(), nullable=False), sa.Column("food_name", sa.String(length=200), nullable=False), sa.Column("quantity", sa.Numeric(precision=10, scale=3), nullable=False), sa.Column("unit", sa.Enum("g", "ml", "serving", "piece", name="food_unit", native_enum=False, create_constraint=True), nullable=False), sa.Column("calories_kcal", sa.Numeric(precision=10, scale=3), nullable=True), sa.Column("protein_g", sa.Numeric(precision=10, scale=3), nullable=True), sa.Column("carbohydrates_g", sa.Numeric(precision=10, scale=3), nullable=True), sa.Column("fat_g", sa.Numeric(precision=10, scale=3), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.CheckConstraint("quantity > 0", name="ck_meal_items_quantity_positive"), sa.CheckConstraint("calories_kcal IS NULL OR calories_kcal >= 0", name="ck_meal_items_calories_non_negative"), sa.CheckConstraint("protein_g IS NULL OR protein_g >= 0", name="ck_meal_items_protein_non_negative"), sa.CheckConstraint("carbohydrates_g IS NULL OR carbohydrates_g >= 0", name="ck_meal_items_carbohydrates_non_negative"), sa.CheckConstraint("fat_g IS NULL OR fat_g >= 0", name="ck_meal_items_fat_non_negative"), sa.ForeignKeyConstraint(["meal_id"], ["meals.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))


def downgrade() -> None:
    op.drop_table("meal_items")
    op.drop_index("ix_meals_user_eaten_at", table_name="meals")
    op.drop_table("meals")
