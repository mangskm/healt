from sqlalchemy.orm import Session

from app.repositories.health import HealthRepository
from app.schemas.health import HealthResponse


class HealthService:
    def __init__(self, db: Session) -> None:
        self._repository = HealthRepository(db)

    def check(self) -> HealthResponse:
        self._repository.database_is_available()
        return HealthResponse(status="ok", database="connected")
