import type { WeightUnit } from "./profile";

export interface MonthlyReport {
  period: { month: string; timezone: string; start_date: string; end_date: string };
  weight: { unit: WeightUnit; measurement_count: number; first: number | null; latest: number | null; minimum: number | null; maximum: number | null; average: number | null; recorded_change: number | null };
  nutrition: { meal_count: number; item_count: number; items_with_any_nutrition: number; nutrition_missing_item_count: number; totals: { calories_kcal: number; protein_g: number; carbohydrates_g: number; fat_g: number } };
  exercise: { distance_unit: "km"; session_count: number; total_duration_minutes: number; distance: number; distance_session_count: number; calories_burned_kcal: number; calories_entered_session_count: number; activity_types: { activity_type: string; session_count: number; duration_minutes: number }[] };
}

export type ExportDataType = "weight" | "meals" | "exercise";
export type ExportRange = "month" | "last_30_days" | "custom";
