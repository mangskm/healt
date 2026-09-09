import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { App } from "../App";
import { ReportsPage } from "./ReportsPage";

const report = {
  period: { month: "2026-09", timezone: "Asia/Bangkok", start_date: "2026-09-01", end_date: "2026-09-30" },
  weight: { unit: "lb", measurement_count: 2, first: 154.32, latest: 152.12, minimum: 152.12, maximum: 154.32, average: 153.22, recorded_change: -2.2 },
  nutrition: { meal_count: 1, item_count: 2, items_with_any_nutrition: 1, nutrition_missing_item_count: 1, totals: { calories_kcal: 200, protein_g: 4, carbohydrates_g: 0, fat_g: 0 } },
  exercise: { distance_unit: "km", session_count: 1, total_duration_minutes: 30, distance: 2, distance_session_count: 1, calories_burned_kcal: 100, calories_entered_session_count: 1, activity_types: [{ activity_type: "walking", session_count: 1, duration_minutes: 30 }] },
};

describe("ReportsPage", () => {
  it("renders a monthly summary and changes month", async () => {
    const fetchMock = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(report) }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<MemoryRouter><ReportsPage /></MemoryRouter>);

    expect(await screen.findByRole("heading", { name: "Reports" })).toBeInTheDocument();
    expect(screen.getByText("Recorded measurements")).toBeInTheDocument();
    expect(screen.getByText(/1 meals/)).toBeInTheDocument();
    expect(screen.getByText(/Asia\/Bangkok/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Previous month" }));
    const requests = fetchMock.mock.calls as unknown as [string][];
    expect(requests.some(([url]) => url.includes("month=2026-08"))).toBe(true);
  });

  it("shows factual empty states and an API error", async () => {
    const empty = { ...report, weight: { ...report.weight, measurement_count: 0, first: null, latest: null, minimum: null, maximum: null, average: null, recorded_change: null }, nutrition: { ...report.nutrition, meal_count: 0, item_count: 0 }, exercise: { ...report.exercise, session_count: 0, activity_types: [] } };
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(empty) })));
    const { unmount } = render(<MemoryRouter><ReportsPage /></MemoryRouter>);
    expect(await screen.findByText("No weight measurements recorded this month.")).toBeInTheDocument();
    expect(screen.getByText("No meals recorded this month.")).toBeInTheDocument();
    expect(screen.getByText("No exercise sessions recorded this month.")).toBeInTheDocument();
    unmount();
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: false })));
    render(<MemoryRouter><ReportsPage /></MemoryRouter>);
    expect(await screen.findByRole("alert")).toHaveTextContent("Report could not be loaded.");
  });

  it("exposes Reports through the protected route and desktop/mobile navigation", async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/auth/me")) return Promise.resolve({ ok: true, json: () => Promise.resolve({ id: "u1", email: "owner@example.com" }) });
      return Promise.resolve({ ok: true, json: () => Promise.resolve(report) });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<MemoryRouter initialEntries={["/reports"]}><App /></MemoryRouter>);

    expect(await screen.findByRole("heading", { name: "Reports" })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Reports" }).length).toBeGreaterThanOrEqual(2);
  });

  it("requests a CSV export using the selected custom range", async () => {
    const createObjectURL = vi.fn(() => "blob:report");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    const fetchMock = vi.fn((url: string) => Promise.resolve(url.includes("/exports/")
      ? { ok: true, blob: () => Promise.resolve(new Blob(["csv"])) }
      : { ok: true, json: () => Promise.resolve(report) }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<MemoryRouter><ReportsPage /></MemoryRouter>);

    await screen.findByRole("button", { name: "Download CSV" });
    await user.selectOptions(screen.getByLabelText("Export data type"), "meals");
    await user.selectOptions(screen.getByLabelText("Export date range"), "custom");
    await user.clear(screen.getByLabelText("Export start date"));
    await user.type(screen.getByLabelText("Export start date"), "2026-09-02");
    await user.clear(screen.getByLabelText("Export end date"));
    await user.type(screen.getByLabelText("Export end date"), "2026-09-03");
    await user.click(screen.getByRole("button", { name: "Download CSV" }));

    await waitFor(() => expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/exports/meals.csv?range=custom&start=2026-09-02&end=2026-09-03"))).toBe(true));
    expect(createObjectURL).toHaveBeenCalled();
    expect(click).toHaveBeenCalled();
    click.mockRestore();
  });
});
