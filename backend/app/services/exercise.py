from uuid import UUID

from sqlalchemy.orm import Session

from app.models.exercise import ExerciseSession
from app.models.user import User
from app.repositories.exercise import ExerciseRepository
from app.schemas.exercise import ExerciseCreate, ExerciseListResponse, ExerciseResponse, ExerciseUpdate
from app.services.distance_units import to_kilometers


class ExerciseNotFoundError(Exception):
    """Raised for a missing or non-owned exercise session."""


class ExerciseService:
    def __init__(self, db: Session, user: User) -> None:
        self._db = db
        self._user = user
        self._sessions = ExerciseRepository(db)

    def list_sessions(self, limit: int, offset: int) -> ExerciseListResponse:
        sessions, total = self._sessions.list_for_user(self._user.id, limit, offset)
        return ExerciseListResponse(items=[ExerciseResponse.model_validate(session) for session in sessions], total=total)

    def get_session(self, session_id: UUID) -> ExerciseResponse:
        return ExerciseResponse.model_validate(self._get_owned_session(session_id))

    def create_session(self, payload: ExerciseCreate) -> ExerciseResponse:
        data = payload.model_dump(exclude={"distance", "distance_unit"})
        session = ExerciseSession(user_id=self._user.id, distance_km=to_kilometers(payload.distance, payload.distance_unit) if payload.distance is not None else None, **data)
        self._sessions.add(session)
        self._sessions.save()
        self._db.refresh(session)
        return ExerciseResponse.model_validate(session)

    def update_session(self, session_id: UUID, payload: ExerciseUpdate) -> ExerciseResponse:
        session = self._get_owned_session(session_id)
        data = payload.model_dump(exclude_unset=True)
        if "distance" in data:
            distance = data.pop("distance")
            unit = data.pop("distance_unit")
            session.distance_km = to_kilometers(distance, unit) if distance is not None else None
        for field_name, value in data.items():
            setattr(session, field_name, value)
        self._sessions.save()
        self._db.refresh(session)
        return ExerciseResponse.model_validate(session)

    def delete_session(self, session_id: UUID) -> None:
        self._sessions.delete(self._get_owned_session(session_id))
        self._sessions.save()

    def _get_owned_session(self, session_id: UUID) -> ExerciseSession:
        session = self._sessions.get_for_user(self._user.id, session_id)
        if session is None:
            raise ExerciseNotFoundError
        return session
