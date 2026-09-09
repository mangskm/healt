import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { TodayPage } from "./TodayPage";
import { AuthProvider } from "../features/auth/AuthContext";

const empty = { timezone: "UTC", date: "2026-09-06", profile: null, latest_weight: null, active_goals: [], meals: { count: 0, item_count: 0, nutrition_item_count: 0, nutrition_missing_item_count: 0, calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 }, exercise: { count: 0, duration_minutes: 0, distance_km: 0, distance_session_count: 0, calories_burned_kcal: 0, calories_entered_session_count: 0 }, reminders: [] };
describe("TodayPage", () => {
  it("shows dashboard empty states", async () => { vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(empty) }))); render(<BrowserRouter><AuthProvider><TodayPage /></AuthProvider></BrowserRouter>); expect(await screen.findByText("No weight records yet.")).toBeInTheDocument(); expect(screen.getByText("No meals today.")).toBeInTheDocument(); expect(screen.getByText("No reminders scheduled for today.")).toBeInTheDocument(); });
  it("shows today's populated reminders", async () => { const dashboard = { ...empty, reminders: [{ id: "r1", reminder_type: "weight", title: "Log weight", reminder_time: "08:00:00", schedule_type: "daily", day_of_week: null, status: "due" }] }; vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(dashboard) }))); render(<BrowserRouter><AuthProvider><TodayPage /></AuthProvider></BrowserRouter>); expect(await screen.findByText((_, node) => node?.tagName === "P" && node.textContent?.includes("Log weight") === true)).toBeInTheDocument(); });
  it("shows an API error instead of crashing when the backend contract is stale", async () => { const stale = { ...empty }; delete (stale as Partial<typeof empty>).reminders; vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(stale) }))); render(<BrowserRouter><AuthProvider><TodayPage /></AuthProvider></BrowserRouter>); expect(await screen.findByRole("alert")).toHaveTextContent("Dashboard could not be loaded."); });
});
