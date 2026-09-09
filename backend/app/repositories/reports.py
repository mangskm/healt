from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.exercise import ExerciseSession
from app.models.meal import Meal
from app.models.weight import WeightRecord


class ReportRepository:
    """Read-only, user-scoped record queries used by reports and exports."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def weight_records_in_range(self, user_id: UUID, start: datetime, end: datetime) -> list[WeightRecord]:
        statement = (
            select(WeightRecord)
            .where(WeightRecord.user_id == user_id, WeightRecord.recorded_at >= start, WeightRecord.recorded_at < end)
            .order_by(WeightRecord.recorded_at.asc(), WeightRecord.created_at.asc())
        )
        return list(self._db.scalars(statement))

    def meals_in_range(self, user_id: UUID, start: datetime, end: datetime) -> list[Meal]:
        statement = (
            select(Meal)
            .options(selectinload(Meal.items))
            .where(Meal.user_id == user_id, Meal.eaten_at >= start, Meal.eaten_at < end)
            .order_by(Meal.eaten_at.asc(), Meal.created_at.asc())
        )
        return list(self._db.scalars(statement))

    def exercise_sessions_in_range(self, user_id: UUID, start: datetime, end: datetime) -> list[ExerciseSession]:
        statement = (
            select(ExerciseSession)
            .where(ExerciseSession.user_id == user_id, ExerciseSession.performed_at >= start, ExerciseSession.performed_at < end)
            .order_by(ExerciseSession.performed_at.asc(), ExerciseSession.created_at.asc())
        )
        return list(self._db.scalars(statement))
