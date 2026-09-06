import type { Profile, ProfileUpdate } from "../types/profile";
import type { WeightRecord, WeightRecordInput, WeightRecordList, WeightRecordUpdate } from "../types/weight";
import type { Goal, GoalInput, GoalUpdate } from "../types/goal";
import type { Meal, MealInput, MealItem, MealItemInput } from "../types/meal";
import type { ExerciseInput, ExerciseSession } from "../types/exercise";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

export async function getHealth(): Promise<{ status: "ok"; database: "connected" }> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);

  if (!response.ok) {
    throw new Error("The API health check failed.");
  }

  return response.json();
}

export async function getProfile(): Promise<Profile | null> {
  const response = await fetch(`${apiBaseUrl}/api/v1/profile`);

  if (response.status === 404) return null;
  if (!response.ok) throw new ApiError(response.status, "The profile could not be loaded.");

  return response.json();
}

export async function updateProfile(profile: ProfileUpdate): Promise<Profile> {
  const response = await fetch(`${apiBaseUrl}/api/v1/profile`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    throw new ApiError(response.status, "The profile could not be saved. Check the values and try again.");
  }
  return response.json();
}

export async function listWeightRecords(): Promise<WeightRecordList> {
  const response = await fetch(`${apiBaseUrl}/api/v1/weight-records?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Weight records could not be loaded.");
  return response.json();
}

export async function createWeightRecord(payload: WeightRecordInput): Promise<WeightRecord> {
  const response = await fetch(`${apiBaseUrl}/api/v1/weight-records`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new ApiError(response.status, "Weight record could not be saved.");
  return response.json();
}

export async function updateWeightRecord(id: string, payload: WeightRecordUpdate): Promise<WeightRecord> {
  const response = await fetch(`${apiBaseUrl}/api/v1/weight-records/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new ApiError(response.status, "Weight record could not be updated.");
  return response.json();
}

export async function deleteWeightRecord(id: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/v1/weight-records/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Weight record could not be deleted.");
}

export async function listGoals(): Promise<{ items: Goal[]; total: number }> {
  const response = await fetch(`${apiBaseUrl}/api/v1/goals?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Goals could not be loaded.");
  return response.json();
}

export async function createGoal(payload: GoalInput): Promise<Goal> {
  const response = await fetch(`${apiBaseUrl}/api/v1/goals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Goal could not be saved.");
  return response.json();
}

export async function updateGoal(id: string, payload: GoalUpdate): Promise<Goal> {
  const response = await fetch(`${apiBaseUrl}/api/v1/goals/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Goal could not be updated.");
  return response.json();
}

export async function deleteGoal(id: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/v1/goals/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Goal could not be deleted.");
}

export async function listMeals(): Promise<{ items: Meal[]; total: number }> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Meals could not be loaded.");
  return response.json();
}

export async function getMeal(id: string): Promise<Meal> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals/${id}`);
  if (!response.ok) throw new ApiError(response.status, "Meal could not be loaded.");
  return response.json();
}

export async function createMeal(payload: MealInput): Promise<Meal> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal could not be saved.");
  return response.json();
}

export async function updateMeal(id: string, payload: Partial<MealInput>): Promise<Meal> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal could not be updated.");
  return response.json();
}

export async function deleteMeal(id: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Meal could not be deleted.");
}

export async function createMealItem(mealId: string, payload: MealItemInput): Promise<MealItem> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals/${mealId}/items`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal item could not be saved.");
  return response.json();
}

export async function updateMealItem(mealId: string, itemId: string, payload: Partial<MealItemInput>): Promise<MealItem> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals/${mealId}/items/${itemId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal item could not be updated.");
  return response.json();
}

export async function deleteMealItem(mealId: string, itemId: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/v1/meals/${mealId}/items/${itemId}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Meal item could not be deleted.");
}

export async function listExerciseSessions(): Promise<{ items: ExerciseSession[]; total: number }> {
  const response = await fetch(`${apiBaseUrl}/api/v1/exercise-sessions?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Exercise sessions could not be loaded.");
  return response.json();
}

export async function createExerciseSession(payload: ExerciseInput): Promise<ExerciseSession> {
  const response = await fetch(`${apiBaseUrl}/api/v1/exercise-sessions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Exercise session could not be saved.");
  return response.json();
}

export async function updateExerciseSession(id: string, payload: Partial<ExerciseInput>): Promise<ExerciseSession> {
  const response = await fetch(`${apiBaseUrl}/api/v1/exercise-sessions/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Exercise session could not be updated.");
  return response.json();
}

export async function deleteExerciseSession(id: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/v1/exercise-sessions/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Exercise session could not be deleted.");
}
