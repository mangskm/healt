import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { GoalsPage } from "./GoalsPage";

function renderPage(fetchMock: ReturnType<typeof vi.fn>) {
  vi.stubGlobal("fetch", fetchMock);
  return render(<BrowserRouter><GoalsPage /></BrowserRouter>);
}

describe("GoalsPage", () => {
  it("shows an empty state", async () => {
    const fetchMock = vi.fn((url: string) => Promise.resolve(url.includes("profile") ? { status: 404, ok: false } : { ok: true, json: () => Promise.resolve(url.includes("goals") ? { items: [], total: 0 } : { items: [], total: 0, latest: null }) }));
    renderPage(fetchMock);
    expect(await screen.findByText("No goals yet. Add a target-weight goal above.")).toBeInTheDocument();
  });

  it("creates a target-weight goal and validates its value", async () => {
    const goal = { id: "goal-1", goal_type: "target_weight", target_value_kg: 68, target_date: null, status: "active", created_at: "2026-09-06T00:00:00Z", updated_at: "2026-09-06T00:00:00Z" };
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("profile")) return Promise.resolve({ status: 404, ok: false });
      if (options?.method === "POST") return Promise.resolve({ ok: true, json: () => Promise.resolve(goal) });
      return Promise.resolve({ ok: true, json: () => Promise.resolve(url.includes("goals") ? { items: [], total: 0 } : { items: [], total: 0, latest: null }) });
    });
    const user = userEvent.setup();
    renderPage(fetchMock);
    await screen.findByText("No goals yet. Add a target-weight goal above.");
    await user.click(screen.getByRole("button", { name: "Save goal" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Enter a target weight greater than zero.");
    await user.type(screen.getByLabelText("Target weight"), "68");
    await user.click(screen.getByRole("button", { name: "Save goal" }));
    expect(await screen.findByText("Goal saved.")).toBeInTheDocument();
  });
});
