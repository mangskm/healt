from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.goal import Goal


class GoalRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: UUID, limit: int, offset: int) -> tuple[list[Goal], int]:
        goals = list(self._db.scalars(select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc()).limit(limit).offset(offset)))
        total = self._db.scalar(select(func.count()).select_from(Goal).where(Goal.user_id == user_id)) or 0
        return goals, total

    def get_for_user(self, user_id: UUID, goal_id: UUID) -> Goal | None:
        return self._db.scalar(select(Goal).where(Goal.user_id == user_id, Goal.id == goal_id))

    def add(self, goal: Goal) -> None:
        self._db.add(goal)

    def delete(self, goal: Goal) -> None:
        self._db.delete(goal)

    def save(self) -> None:
        self._db.commit()
