from sqlalchemy.orm import Session

from app.models.weight import WeightRecord
from app.repositories.user import UserRepository
from app.repositories.weight import WeightRecordRepository
from app.schemas.weight import WeightRecordCreate, WeightRecordListResponse, WeightRecordResponse, WeightRecordUpdate
from app.services.weight_units import to_kilograms


class WeightRecordNotFoundError(Exception):
    """Raised when a requested record is missing or owned by another user."""


class WeightRecordService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._records = WeightRecordRepository(db)

    def list_records(self, limit: int, offset: int) -> WeightRecordListResponse:
        user = self._users.get_or_create_local_user()
        records, total = self._records.list_for_user(user.id, limit, offset)
        latest = self._records.latest_for_user(user.id)
        return WeightRecordListResponse(items=[WeightRecordResponse.model_validate(record) for record in records], total=total, latest=WeightRecordResponse.model_validate(latest) if latest else None)

    def get_record(self, record_id) -> WeightRecordResponse:
        user = self._users.get_or_create_local_user()
        record = self._records.get_for_user(user.id, record_id)
        if record is None:
            raise WeightRecordNotFoundError
        return WeightRecordResponse.model_validate(record)

    def create_record(self, payload: WeightRecordCreate) -> WeightRecordResponse:
        user = self._users.get_or_create_local_user()
        record = WeightRecord(user_id=user.id, weight_kg=to_kilograms(payload.weight, payload.unit), recorded_at=payload.recorded_at, note=payload.note)
        self._records.add(record)
        self._records.save()
        self._db.refresh(record)
        return WeightRecordResponse.model_validate(record)

    def update_record(self, record_id, payload: WeightRecordUpdate) -> WeightRecordResponse:
        user = self._users.get_or_create_local_user()
        record = self._records.get_for_user(user.id, record_id)
        if record is None:
            raise WeightRecordNotFoundError
        data = payload.model_dump(exclude_unset=True)
        if "weight" in data:
            record.weight_kg = to_kilograms(data.pop("weight"), data.pop("unit"))
        for field_name, value in data.items():
            setattr(record, field_name, value)
        self._records.save()
        self._db.refresh(record)
        return WeightRecordResponse.model_validate(record)

    def delete_record(self, record_id) -> None:
        user = self._users.get_or_create_local_user()
        record = self._records.get_for_user(user.id, record_id)
        if record is None:
            raise WeightRecordNotFoundError
        self._records.delete(record)
        self._records.save()
