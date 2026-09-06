import type { WeightUnit } from "./profile";

export type GoalType = "target_weight";
export type GoalStatus = "active" | "completed" | "cancelled";

export interface Goal {
  id: string;
  goal_type: GoalType;
  target_value_kg: number;
  target_date: string | null;
  status: GoalStatus;
  created_at: string;
  updated_at: string;
}

export interface GoalInput {
  goal_type: GoalType;
  target_value: number;
  unit: WeightUnit;
  target_date?: string | null;
  status?: GoalStatus;
}

export type GoalUpdate = Partial<Omit<GoalInput, "goal_type">>;
