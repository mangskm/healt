from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics import AnalyticsService
router=APIRouter(prefix='/analytics',tags=['analytics'])
@router.get('',response_model=AnalyticsResponse)
def analytics(period:str='7d',db:Session=Depends(get_db),user: User = Depends(get_current_user)):
    try:return AnalyticsService(db, user).get(period)
    except ValueError as e: raise HTTPException(422,detail=str(e)) from e
