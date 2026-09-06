from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.weight import WeightRecord


class WeightRecordRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: UUID, limit: int, offset: int) -> tuple[list[WeightRecord], int]:
        ordering = (WeightRecord.recorded_at.desc(), WeightRecord.created_at.desc())
        records = list(self._db.scalars(select(WeightRecord).where(WeightRecord.user_id == user_id).order_by(*ordering).limit(limit).offset(offset)))
        total = self._db.scalar(select(func.count()).select_from(WeightRecord).where(WeightRecord.user_id == user_id)) or 0
        return records, total

    def latest_for_user(self, user_id: UUID) -> WeightRecord | None:
        return self._db.scalar(select(WeightRecord).where(WeightRecord.user_id == user_id).order_by(WeightRecord.recorded_at.desc(), WeightRecord.created_at.desc()).limit(1))

    def get_for_user(self, user_id: UUID, record_id: UUID) -> WeightRecord | None:
        return self._db.scalar(select(WeightRecord).where(WeightRecord.user_id == user_id, WeightRecord.id == record_id))

    def add(self, record: WeightRecord) -> None:
        self._db.add(record)

    def delete(self, record: WeightRecord) -> None:
        self._db.delete(record)

    def save(self) -> None:
        self._db.commit()
