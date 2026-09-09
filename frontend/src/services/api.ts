import type { Profile, ProfileUpdate } from "../types/profile";
import type { WeightRecord, WeightRecordInput, WeightRecordList, WeightRecordUpdate } from "../types/weight";
import type { Goal, GoalInput, GoalUpdate } from "../types/goal";
import type { Meal, MealInput, MealItem, MealItemInput } from "../types/meal";
import type { ExerciseInput, ExerciseSession } from "../types/exercise";
import type { Reminder, ReminderInput, TodayNotifications } from "../types/reminder";

export interface Dashboard { timezone: string; date: string; profile: { preferred_name: string | null; weight_unit: string | null } | null; latest_weight: { weight_kg: number; recorded_at: string } | null; active_goals: { id: string; target_value_kg: number; target_date: string | null; status: string }[]; meals: { count: number; item_count: number; nutrition_item_count: number; nutrition_missing_item_count: number; calories_kcal: number; protein_g: number; carbohydrates_g: number; fat_g: number }; exercise: { count: number; duration_minutes: number; distance_km: number; distance_session_count: number; calories_burned_kcal: number; calories_entered_session_count: number }; reminders: { id: string; reminder_type: string; title: string; reminder_time: string; schedule_type: string; day_of_week: number | null; status: "upcoming" | "due" }[]; }

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://localhost:8000" : "");
const unauthorizedEvent = "health-app:unauthorized";

async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const response = await fetch(input, { ...init, credentials: "include" });
  if (response.status === 401 && typeof window !== "undefined") {
    window.dispatchEvent(new Event(unauthorizedEvent));
  }
  return response;
}

export { unauthorizedEvent };

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

export interface AuthUser {
  id: string;
  email: string;
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new ApiError(response.status, "Invalid email or password.");
  return (await response.json() as { user: AuthUser }).user;
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/auth/me`);
  if (response.status === 401) return null;
  if (!response.ok) throw new ApiError(response.status, "The current session could not be verified.");
  return response.json();
}

export async function logout(): Promise<void> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/auth/logout`, { method: "POST" });
  if (!response.ok) throw new ApiError(response.status, "Logout failed.");
}

export async function getHealth(): Promise<{ status: "ok"; database: "connected" }> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/health`);

  if (!response.ok) {
    throw new Error("The API health check failed.");
  }

  return response.json();
}

export async function getProfile(): Promise<Profile | null> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/profile`);

  if (response.status === 404) return null;
  if (!response.ok) throw new ApiError(response.status, "The profile could not be loaded.");

  return response.json();
}

export async function updateProfile(profile: ProfileUpdate): Promise<Profile> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/profile`, {
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
  const response = await apiFetch(`${apiBaseUrl}/api/v1/weight-records?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Weight records could not be loaded.");
  return response.json();
}

export async function createWeightRecord(payload: WeightRecordInput): Promise<WeightRecord> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/weight-records`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new ApiError(response.status, "Weight record could not be saved.");
  return response.json();
}

export async function updateWeightRecord(id: string, payload: WeightRecordUpdate): Promise<WeightRecord> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/weight-records/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new ApiError(response.status, "Weight record could not be updated.");
  return response.json();
}

export async function deleteWeightRecord(id: string): Promise<void> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/weight-records/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Weight record could not be deleted.");
}

export async function listGoals(): Promise<{ items: Goal[]; total: number }> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/goals?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Goals could not be loaded.");
  return response.json();
}

export async function createGoal(payload: GoalInput): Promise<Goal> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/goals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Goal could not be saved.");
  return response.json();
}

export async function updateGoal(id: string, payload: GoalUpdate): Promise<Goal> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/goals/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Goal could not be updated.");
  return response.json();
}

export async function deleteGoal(id: string): Promise<void> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/goals/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Goal could not be deleted.");
}

export async function listMeals(): Promise<{ items: Meal[]; total: number }> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Meals could not be loaded.");
  return response.json();
}

export async function getMeal(id: string): Promise<Meal> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals/${id}`);
  if (!response.ok) throw new ApiError(response.status, "Meal could not be loaded.");
  return response.json();
}

export async function createMeal(payload: MealInput): Promise<Meal> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal could not be saved.");
  return response.json();
}

export async function updateMeal(id: string, payload: Partial<MealInput>): Promise<Meal> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal could not be updated.");
  return response.json();
}

export async function deleteMeal(id: string): Promise<void> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Meal could not be deleted.");
}

export async function createMealItem(mealId: string, payload: MealItemInput): Promise<MealItem> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals/${mealId}/items`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal item could not be saved.");
  return response.json();
}

export async function updateMealItem(mealId: string, itemId: string, payload: Partial<MealItemInput>): Promise<MealItem> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals/${mealId}/items/${itemId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Meal item could not be updated.");
  return response.json();
}

export async function deleteMealItem(mealId: string, itemId: string): Promise<void> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/meals/${mealId}/items/${itemId}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Meal item could not be deleted.");
}

export async function listExerciseSessions(): Promise<{ items: ExerciseSession[]; total: number }> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/exercise-sessions?limit=50&offset=0`);
  if (!response.ok) throw new ApiError(response.status, "Exercise sessions could not be loaded.");
  return response.json();
}

export async function createExerciseSession(payload: ExerciseInput): Promise<ExerciseSession> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/exercise-sessions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Exercise session could not be saved.");
  return response.json();
}

export async function updateExerciseSession(id: string, payload: Partial<ExerciseInput>): Promise<ExerciseSession> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/exercise-sessions/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new ApiError(response.status, "Exercise session could not be updated.");
  return response.json();
}

export async function deleteExerciseSession(id: string): Promise<void> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/exercise-sessions/${id}`, { method: "DELETE" });
  if (!response.ok) throw new ApiError(response.status, "Exercise session could not be deleted.");
}

export async function getDashboard(): Promise<Dashboard> {
  const response = await apiFetch(`${apiBaseUrl}/api/v1/dashboard`);
  if (!response.ok) throw new ApiError(response.status, "Dashboard could not be loaded.");
  const dashboard: unknown = await response.json();
  if (!dashboard || typeof dashboard !== "object" || !Array.isArray((dashboard as { reminders?: unknown }).reminders)) {
    throw new ApiError(response.status, "The Dashboard API response is missing reminders. Restart the current Phase 8 backend after applying its migration.");
  }
  return dashboard as Dashboard;
}
export async function getAnalytics(period: "7d" | "30d") { const response=await apiFetch(`${apiBaseUrl}/api/v1/analytics?period=${period}`); if(!response.ok) throw new ApiError(response.status,"Analytics could not be loaded."); return response.json(); }
export async function listReminders(): Promise<{ items: Reminder[]; total: number }> { const response = await apiFetch(`${apiBaseUrl}/api/v1/reminders`); if (!response.ok) throw new ApiError(response.status, "Reminders could not be loaded."); return response.json(); }
export async function createReminder(payload: ReminderInput): Promise<Reminder> { const response = await apiFetch(`${apiBaseUrl}/api/v1/reminders`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!response.ok) throw new ApiError(response.status, "Reminder could not be saved."); return response.json(); }
export async function updateReminder(id: string, payload: Partial<ReminderInput>): Promise<Reminder> { const response = await apiFetch(`${apiBaseUrl}/api/v1/reminders/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!response.ok) throw new ApiError(response.status, "Reminder could not be updated."); return response.json(); }
export async function deleteReminder(id: string): Promise<void> { const response = await apiFetch(`${apiBaseUrl}/api/v1/reminders/${id}`, { method: "DELETE" }); if (!response.ok) throw new ApiError(response.status, "Reminder could not be deleted."); }
export async function getTodayNotifications(): Promise<TodayNotifications> { const response = await apiFetch(`${apiBaseUrl}/api/v1/notifications/today`); if (!response.ok) throw new ApiError(response.status, "Today's reminders could not be loaded."); return response.json(); }
