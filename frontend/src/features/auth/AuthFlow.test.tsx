import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../App";

const response = (status: number, body: unknown) => ({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) });

afterEach(() => vi.unstubAllGlobals());

describe("Phase 9 authentication flow", () => {
  it("redirects an anonymous visitor to the login page", async () => {
    const fetchMock = vi.fn(() => Promise.resolve(response(401, { detail: "Authentication required." })));
    vi.stubGlobal("fetch", fetchMock);
    render(<MemoryRouter initialEntries={["/weight"]}><App /></MemoryRouter>);

    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
    const firstCall = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(firstCall[1]).toMatchObject({ credentials: "include" });
  });

  it("logs in and reaches the protected dashboard", async () => {
    const emptyDashboard = { timezone: "UTC", date: "2026-09-07", profile: null, latest_weight: null, active_goals: [], meals: { count: 0, item_count: 0, nutrition_item_count: 0, nutrition_missing_item_count: 0, calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 }, exercise: { count: 0, duration_minutes: 0, distance_km: 0, distance_session_count: 0, calories_burned_kcal: 0, calories_entered_session_count: 0 }, reminders: [] };
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/auth/me")) return Promise.resolve(response(401, {}));
      if (url.includes("/auth/login")) return Promise.resolve(response(200, { user: { id: "u1", email: "owner@example.com" } }));
      if (url.includes("/dashboard")) return Promise.resolve(response(200, emptyDashboard));
      return Promise.resolve(response(200, { status: "ok", database: "connected" }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<MemoryRouter initialEntries={["/login"]}><App /></MemoryRouter>);

    await user.type(await screen.findByLabelText("Email"), "owner@example.com");
    await user.type(screen.getByLabelText("Password"), "safe password");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("heading", { name: "Today" })).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/auth/login"))).toBe(true);
  });

  it("recovers centrally from an expired session", async () => {
    const emptyDashboard = { timezone: "UTC", date: "2026-09-07", profile: null, latest_weight: null, active_goals: [], meals: { count: 0, item_count: 0, nutrition_item_count: 0, nutrition_missing_item_count: 0, calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 }, exercise: { count: 0, duration_minutes: 0, distance_km: 0, distance_session_count: 0, calories_burned_kcal: 0, calories_entered_session_count: 0 }, reminders: [] };
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/auth/me")) return Promise.resolve(response(200, { id: "u1", email: "owner@example.com" }));
      if (url.includes("/dashboard")) return Promise.resolve(response(200, emptyDashboard));
      return Promise.resolve(response(200, { status: "ok", database: "connected" }));
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);

    await screen.findByRole("heading", { name: "Today" });
    await act(async () => window.dispatchEvent(new Event("health-app:unauthorized")));
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
  });

  it("logs out through the API and returns to login", async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/auth/me")) return Promise.resolve(response(200, { id: "u1", email: "owner@example.com" }));
      if (url.includes("/auth/logout")) return Promise.resolve(response(204, {}));
      if (url.includes("/dashboard")) return Promise.resolve(response(200, { timezone: "UTC", date: "2026-09-07", profile: null, latest_weight: null, active_goals: [], meals: { count: 0, item_count: 0, nutrition_item_count: 0, nutrition_missing_item_count: 0, calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 }, exercise: { count: 0, duration_minutes: 0, distance_km: 0, distance_session_count: 0, calories_burned_kcal: 0, calories_entered_session_count: 0 }, reminders: [] }));
      return Promise.resolve(response(200, { status: "ok", database: "connected" }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);

    await screen.findByRole("heading", { name: "Today" });
    await user.click(screen.getByRole("button", { name: "Sign out" }));
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/auth/logout"))).toBe(true);
  });
});
