export type MealType = "breakfast" | "lunch" | "dinner" | "snack" | "other";
export type FoodUnit = "g" | "ml" | "serving" | "piece";

export interface MealItem {
  id: string;
  food_name: string;
  quantity: number;
  unit: FoodUnit;
  calories_kcal: number | null;
  protein_g: number | null;
  carbohydrates_g: number | null;
  fat_g: number | null;
  created_at: string;
  updated_at: string;
}

export interface Meal {
  id: string;
  meal_type: MealType;
  eaten_at: string;
  note: string | null;
  created_at: string;
  updated_at: string;
  items: MealItem[];
}

export interface MealInput {
  meal_type: MealType;
  eaten_at: string;
  note?: string | null;
}

export interface MealItemInput {
  food_name: string;
  quantity: number;
  unit: FoodUnit;
  calories_kcal?: number | null;
  protein_g?: number | null;
  carbohydrates_g?: number | null;
  fat_g?: number | null;
}
