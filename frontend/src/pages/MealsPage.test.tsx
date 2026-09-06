import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { MealsPage } from "./MealsPage";

const meal = { id: "meal-1", meal_type: "lunch", eaten_at: "2026-09-06T10:00:00Z", note: "Packed", created_at: "2026-09-06T10:00:00Z", updated_at: "2026-09-06T10:00:00Z", items: [{ id: "item-1", food_name: "Rice", quantity: 150, unit: "g", calories_kcal: 240, protein_g: 4.5, carbohydrates_g: 52, fat_g: 0.5, created_at: "", updated_at: "" }] };

function renderPage(fetchMock: ReturnType<typeof vi.fn>) {
  vi.stubGlobal("fetch", fetchMock);
  return render(<BrowserRouter><MealsPage /></BrowserRouter>);
}

describe("MealsPage", () => {
  it("shows an empty state", async () => {
    renderPage(vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0 }) })));
    expect(await screen.findByText("No meals yet. Add a meal above.")).toBeInTheDocument();
  });

  it("displays entered nutrition values and deletes a meal", async () => {
    const fetchMock = vi.fn((_: string, options?: RequestInit) => Promise.resolve(options?.method === "DELETE" ? { ok: true } : { ok: true, json: () => Promise.resolve({ items: [meal], total: 1 }) }));
    const user = userEvent.setup();
    renderPage(fetchMock);
    expect(await screen.findByText(/Rice \(150 g\)/)).toBeInTheDocument();
    expect(screen.getByText(/Calories: 240 kcal/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Delete" }));
    expect(await screen.findByText("Meal deleted.")).toBeInTheDocument();
  });

  it("adds multiple food items and validates client input", async () => {
    const savedMeal = { ...meal, items: [] };
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (options?.method === "POST" && url.endsWith("/meals")) return Promise.resolve({ ok: true, json: () => Promise.resolve(savedMeal) });
      if (options?.method === "POST") return Promise.resolve({ ok: true, json: () => Promise.resolve(meal.items[0]) });
      if (url.endsWith("/meal-1")) return Promise.resolve({ ok: true, json: () => Promise.resolve(meal) });
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0 }) });
    });
    const user = userEvent.setup();
    renderPage(fetchMock);
    await screen.findByText("No meals yet. Add a meal above.");
    await user.click(screen.getByRole("button", { name: "Save meal" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Each food item needs a name.");
    await user.type(screen.getByLabelText("Food name 1"), "Rice");
    await user.type(screen.getByLabelText("Quantity 1"), "150");
    await user.click(screen.getByRole("button", { name: "Add food item" }));
    await user.type(screen.getByLabelText("Food name 2"), "Tofu");
    await user.type(screen.getByLabelText("Quantity 2"), "100");
    await user.click(screen.getByRole("button", { name: "Save meal" }));
    expect(await screen.findByText("Meal saved.")).toBeInTheDocument();
    expect(fetchMock.mock.calls.filter(([, options]) => (options as RequestInit | undefined)?.method === "POST")).toHaveLength(3);
  });

  it("loads an existing meal into the edit form", async () => {
    renderPage(vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [meal], total: 1 }) })));
    const user = userEvent.setup();
    await screen.findByText(/Rice \(150 g\)/);
    await user.click(screen.getByRole("button", { name: "Edit" }));
    expect(screen.getByRole("heading", { name: "Edit meal" })).toBeInTheDocument();
    expect(screen.getByLabelText("Food name 1")).toHaveValue("Rice");
  });
});
