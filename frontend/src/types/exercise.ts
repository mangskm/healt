export type ActivityType = "walking" | "running" | "cycling" | "strength_training" | "swimming" | "sports" | "other";
export type DistanceUnit = "km" | "mi";

export interface ExerciseSession { id: string; activity_type: ActivityType; performed_at: string; duration_minutes: number; distance_km: number | null; calories_burned_kcal: number | null; note: string | null; created_at: string; updated_at: string; }
export interface ExerciseInput { activity_type: ActivityType; performed_at: string; duration_minutes: number; distance?: number | null; distance_unit?: DistanceUnit | null; calories_burned_kcal?: number | null; note?: string | null; }
