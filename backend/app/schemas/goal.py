from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.goal import GoalStatus, GoalType
from app.models.profile import WeightUnit


class GoalCreate(BaseModel):
    goal_type: GoalType
    target_value: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    unit: WeightUnit
    target_date: date | None = None
    status: GoalStatus = GoalStatus.ACTIVE


class GoalUpdate(BaseModel):
    target_value: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    unit: WeightUnit | None = None
    target_date: date | None = None
    status: GoalStatus | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "GoalUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one goal field to update.")
        if ("target_value" in self.model_fields_set) != ("unit" in self.model_fields_set):
            raise ValueError("Target value and unit must be supplied together.")
        return self


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal_type: GoalType
    target_value_kg: float
    target_date: date | None
    status: GoalStatus
    created_at: datetime
    updated_at: datetime


class GoalListResponse(BaseModel):
    items: list[GoalResponse]
    total: int
