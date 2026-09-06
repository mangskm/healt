from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.profile import router as profile_router
from app.api.v1.weight import router as weight_router
from app.api.v1.goals import router as goals_router
from app.api.v1.meals import router as meals_router
from app.api.v1.exercise import router as exercise_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(profile_router)
api_router.include_router(weight_router)
api_router.include_router(goals_router)
api_router.include_router(meals_router)
api_router.include_router(exercise_router)
