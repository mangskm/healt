from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.reminder import Reminder


class ReminderRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: UUID) -> tuple[list[Reminder], int]:
        statement = select(Reminder).where(Reminder.user_id == user_id).order_by(Reminder.reminder_time, Reminder.created_at)
        return list(self._db.scalars(statement)), self._db.scalar(select(func.count()).select_from(Reminder).where(Reminder.user_id == user_id)) or 0

    def get_for_user(self, user_id: UUID, reminder_id: UUID) -> Reminder | None:
        return self._db.scalar(select(Reminder).where(Reminder.user_id == user_id, Reminder.id == reminder_id))

    def list_enabled_for_user(self, user_id: UUID) -> list[Reminder]:
        return list(self._db.scalars(select(Reminder).where(Reminder.user_id == user_id, Reminder.enabled.is_(True)).order_by(Reminder.reminder_time, Reminder.created_at)))

    def add(self, reminder: Reminder) -> None:
        self._db.add(reminder)

    def delete(self, reminder: Reminder) -> None:
        self._db.delete(reminder)

    def save(self) -> None:
        self._db.commit()
