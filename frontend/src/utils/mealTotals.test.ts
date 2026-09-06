import { describe, expect, it } from "vitest";

import { calculateMealTotals } from "./mealTotals";

describe("calculateMealTotals", () => {
  it("sums only nutrition values entered for a meal", () => {
    const totals = calculateMealTotals([
      { id: "1", food_name: "Rice", quantity: 100, unit: "g", calories_kcal: 130, protein_g: 2.5, carbohydrates_g: 28, fat_g: null, created_at: "", updated_at: "" },
      { id: "2", food_name: "Tofu", quantity: 1, unit: "serving", calories_kcal: 80, protein_g: 8, carbohydrates_g: null, fat_g: 4, created_at: "", updated_at: "" },
    ]);

    expect(totals).toEqual({ calories_kcal: 210, protein_g: 10.5, carbohydrates_g: 28, fat_g: 4 });
  });
});
