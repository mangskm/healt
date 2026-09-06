from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.weight import WeightRecordCreate, WeightRecordListResponse, WeightRecordResponse, WeightRecordUpdate
from app.services.weight import WeightRecordNotFoundError, WeightRecordService

router = APIRouter(prefix="/weight-records", tags=["weight records"])


def not_found(error: WeightRecordNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight record not found.")


@router.get("", response_model=WeightRecordListResponse)
def list_weight_records(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)) -> WeightRecordListResponse:
    """List local-user records, newest measurement first."""
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="Limit must be between 1 and 100.")
    if offset < 0:
        raise HTTPException(status_code=422, detail="Offset cannot be negative.")
    return WeightRecordService(db).list_records(limit, offset)


@router.post("", response_model=WeightRecordResponse, status_code=status.HTTP_201_CREATED)
def create_weight_record(payload: WeightRecordCreate, db: Session = Depends(get_db)) -> WeightRecordResponse:
    return WeightRecordService(db).create_record(payload)


@router.get("/{record_id}", response_model=WeightRecordResponse)
def get_weight_record(record_id: UUID, db: Session = Depends(get_db)) -> WeightRecordResponse:
    try:
        return WeightRecordService(db).get_record(record_id)
    except WeightRecordNotFoundError as error:
        raise not_found(error) from error


@router.patch("/{record_id}", response_model=WeightRecordResponse)
def update_weight_record(record_id: UUID, payload: WeightRecordUpdate, db: Session = Depends(get_db)) -> WeightRecordResponse:
    try:
        return WeightRecordService(db).update_record(record_id, payload)
    except WeightRecordNotFoundError as error:
        raise not_found(error) from error


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight_record(record_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        WeightRecordService(db).delete_record(record_id)
    except WeightRecordNotFoundError as error:
        raise not_found(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
