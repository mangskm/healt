from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.health import HealthResponse
from app.services.health import HealthService

router = APIRouter(tags=["health"])


@router.get("/live")
def get_live() -> dict[str, str]:
    """Liveness: the FastAPI process can serve requests without a database query."""
    return {"status": "ok"}


@router.get("/ready", response_model=HealthResponse)
def get_ready(db: Session = Depends(get_db)) -> HealthResponse:
    """Readiness: the process can query its configured database."""
    return HealthService(db).check()


@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)) -> HealthResponse:
    """Return API and database availability for service monitoring."""
    return HealthService(db).check()
