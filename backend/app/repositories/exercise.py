from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.exercise import ExerciseSession


class ExerciseRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: UUID, limit: int, offset: int) -> tuple[list[ExerciseSession], int]:
        sessions = list(self._db.scalars(select(ExerciseSession).where(ExerciseSession.user_id == user_id).order_by(ExerciseSession.performed_at.desc(), ExerciseSession.created_at.desc()).limit(limit).offset(offset)))
        total = self._db.scalar(select(func.count()).select_from(ExerciseSession).where(ExerciseSession.user_id == user_id)) or 0
        return sessions, total

    def get_for_user(self, user_id: UUID, session_id: UUID) -> ExerciseSession | None:
        return self._db.scalar(select(ExerciseSession).where(ExerciseSession.user_id == user_id, ExerciseSession.id == session_id))

    def add(self, session: ExerciseSession) -> None:
        self._db.add(session)

    def delete(self, session: ExerciseSession) -> None:
        self._db.delete(session)

    def save(self) -> None:
        self._db.commit()
