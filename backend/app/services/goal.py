from uuid import UUID

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.repositories.goal import GoalRepository
from app.repositories.user import UserRepository
from app.schemas.goal import GoalCreate, GoalListResponse, GoalResponse, GoalUpdate
from app.services.weight_units import to_kilograms


class GoalNotFoundError(Exception):
    """Raised for a missing or non-owned goal."""


class GoalService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._goals = GoalRepository(db)

    def list_goals(self, limit: int, offset: int) -> GoalListResponse:
        user = self._users.get_or_create_local_user()
        goals, total = self._goals.list_for_user(user.id, limit, offset)
        return GoalListResponse(items=[GoalResponse.model_validate(goal) for goal in goals], total=total)

    def get_goal(self, goal_id: UUID) -> GoalResponse:
        goal = self._get_owned_goal(goal_id)
        return GoalResponse.model_validate(goal)

    def create_goal(self, payload: GoalCreate) -> GoalResponse:
        user = self._users.get_or_create_local_user()
        goal = Goal(user_id=user.id, goal_type=payload.goal_type, target_value_kg=to_kilograms(payload.target_value, payload.unit), target_date=payload.target_date, status=payload.status)
        self._goals.add(goal)
        self._goals.save()
        self._db.refresh(goal)
        return GoalResponse.model_validate(goal)

    def update_goal(self, goal_id: UUID, payload: GoalUpdate) -> GoalResponse:
        goal = self._get_owned_goal(goal_id)
        data = payload.model_dump(exclude_unset=True)
        if "target_value" in data:
            goal.target_value_kg = to_kilograms(data.pop("target_value"), data.pop("unit"))
        for field_name, value in data.items():
            setattr(goal, field_name, value)
        self._goals.save()
        self._db.refresh(goal)
        return GoalResponse.model_validate(goal)

    def delete_goal(self, goal_id: UUID) -> None:
        goal = self._get_owned_goal(goal_id)
        self._goals.delete(goal)
        self._goals.save()

    def _get_owned_goal(self, goal_id: UUID) -> Goal:
        user = self._users.get_or_create_local_user()
        goal = self._goals.get_for_user(user.id, goal_id)
        if goal is None:
            raise GoalNotFoundError
        return goal
