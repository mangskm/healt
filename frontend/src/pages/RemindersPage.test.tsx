import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { RemindersPage } from "./RemindersPage";

const reminder = { id: "reminder-1", reminder_type: "weight", title: "Log weight", reminder_time: "08:00:00", schedule_type: "daily", day_of_week: null, enabled: true, note: null, created_at: "", updated_at: "" };
const renderPage = (fetchMock: ReturnType<typeof vi.fn>) => { vi.stubGlobal("fetch", fetchMock); return render(<BrowserRouter><RemindersPage /></BrowserRouter>); };

describe("RemindersPage", () => {
  it("shows loading then an empty state", async () => { renderPage(vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0 }) }))); expect(await screen.findByText("No reminders yet. Add one above.")).toBeInTheDocument(); });
  it("shows conditional weekly fields and client validation", async () => { const user = userEvent.setup(); renderPage(vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0 }) }))); await screen.findByText("No reminders yet. Add one above."); await user.selectOptions(screen.getByLabelText("Schedule"), "weekly"); expect(screen.getByLabelText("Weekday")).toBeInTheDocument(); await user.click(screen.getByRole("button", { name: "Save reminder" })); expect(await screen.findByRole("alert")).toHaveTextContent("Enter a reminder title."); });
  it("creates, disables, and renders a reminder", async () => { const fetchMock = vi.fn((_: string, options?: RequestInit) => Promise.resolve(options?.method === "POST" || options?.method === "PATCH" ? { ok: true, json: () => Promise.resolve({ ...reminder, enabled: options?.method === "PATCH" ? false : true }) } : { ok: true, json: () => Promise.resolve({ items: [reminder], total: 1 }) })); const user = userEvent.setup(); renderPage(fetchMock); expect(await screen.findByText(/08:00 · Log weight/)).toBeInTheDocument(); await user.click(screen.getByRole("button", { name: "Disable" })); expect(await screen.findByRole("button", { name: "Enable" })).toBeInTheDocument(); });
  it("shows an API error", async () => { renderPage(vi.fn(() => Promise.resolve({ ok: false }))); expect(await screen.findByRole("alert")).toHaveTextContent("Reminders could not be loaded."); });
});
