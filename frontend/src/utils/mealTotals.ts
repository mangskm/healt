import type { MealItem } from "../types/meal";

export interface MealTotals { calories_kcal: number; protein_g: number; carbohydrates_g: number; fat_g: number; }

export function calculateMealTotals(items: MealItem[]): MealTotals {
  return items.reduce<MealTotals>((totals, item) => ({
    calories_kcal: totals.calories_kcal + (item.calories_kcal ?? 0),
    protein_g: totals.protein_g + (item.protein_g ?? 0),
    carbohydrates_g: totals.carbohydrates_g + (item.carbohydrates_g ?? 0),
    fat_g: totals.fat_g + (item.fat_g ?? 0),
  }), { calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 });
}
