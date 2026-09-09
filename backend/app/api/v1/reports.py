from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.reports import MonthlyReportResponse
from app.services.exports import ExportService
from app.services.reports import ReportService

router = APIRouter(tags=["reports"])


@router.get("/reports/monthly", response_model=MonthlyReportResponse)
def monthly_report(
    month: str | None = Query(default=None, description="Local calendar month in YYYY-MM format."),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MonthlyReportResponse:
    try:
        return ReportService(db, user).monthly(month)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/exports/{data_type}.csv")
def export_csv(
    data_type: Literal["weight", "meals", "exercise"],
    range_type: Literal["month", "last_30_days", "custom"] = Query(default="month", alias="range"),
    month: str | None = None,
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    try:
        content, filename = ExportService(db, user).create_csv(data_type, range_type, month, start, end)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return Response(
        content=("\ufeff" + content).encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
