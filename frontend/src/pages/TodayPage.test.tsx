import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { TodayPage } from "./TodayPage";

const empty = { timezone: "UTC", date: "2026-09-06", profile: null, latest_weight: null, active_goals: [], meals: { count: 0, item_count: 0, nutrition_item_count: 0, nutrition_missing_item_count: 0, calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 }, exercise: { count: 0, duration_minutes: 0, distance_km: 0, distance_session_count: 0, calories_burned_kcal: 0, calories_entered_session_count: 0 } };
describe("TodayPage", () => {
  it("shows dashboard empty states", async () => { vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(empty) }))); render(<BrowserRouter><TodayPage /></BrowserRouter>); expect(await screen.findByText("No weight records yet.")).toBeInTheDocument(); expect(screen.getByText("No meals today.")).toBeInTheDocument(); });
});
