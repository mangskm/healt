import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { WeightPage } from "./WeightPage";

function renderPage(fetchMock: ReturnType<typeof vi.fn>) {
  vi.stubGlobal("fetch", fetchMock);
  return render(<BrowserRouter><WeightPage /></BrowserRouter>);
}

describe("WeightPage", () => {
  it("shows an empty state", async () => {
    const fetchMock = vi.fn((url: string) => Promise.resolve(url.includes("profile") ? { status: 404, ok: false } : { ok: true, json: () => Promise.resolve({ items: [], total: 0, latest: null }) }));
    renderPage(fetchMock);

    expect(await screen.findByText("No weight records yet. Add your first measurement above.")).toBeInTheDocument();
  });

  it("displays records and saves a new measurement", async () => {
    const savedRecord = { id: "record-2", weight_kg: 71, recorded_at: "2026-08-10T08:30:00Z", note: null, created_at: "2026-08-10T08:30:00Z", updated_at: "2026-08-10T08:30:00Z" };
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("profile")) return Promise.resolve({ status: 404, ok: false });
      if (options?.method === "POST") return Promise.resolve({ ok: true, json: () => Promise.resolve(savedRecord) });
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [{ ...savedRecord, id: "record-1", weight_kg: 70 }], total: 1, latest: { ...savedRecord, id: "record-1", weight_kg: 70 } }) });
    });
    const user = userEvent.setup();
    renderPage(fetchMock);

    expect((await screen.findAllByText("70.00 kg")).length).toBe(2);
    await user.type(screen.getByLabelText("Weight"), "71");
    await user.click(screen.getByRole("button", { name: "Save record" }));

    expect(await screen.findByText("Weight record saved.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining("/api/v1/weight-records"), expect.objectContaining({ method: "POST" }));
  });

  it("shows client-side validation for an invalid weight", async () => {
    const fetchMock = vi.fn((url: string) => Promise.resolve(url.includes("profile") ? { status: 404, ok: false } : { ok: true, json: () => Promise.resolve({ items: [], total: 0, latest: null }) }));
    const user = userEvent.setup();
    renderPage(fetchMock);

    await screen.findByText("No weight records yet. Add your first measurement above.");
    await user.type(screen.getByLabelText("Weight"), "0");
    await user.click(screen.getByRole("button", { name: "Save record" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Enter a weight greater than zero.");
  });

  it("deletes a displayed record", async () => {
    const record = { id: "record-1", weight_kg: 70, recorded_at: "2026-08-10T08:30:00Z", note: null, created_at: "2026-08-10T08:30:00Z", updated_at: "2026-08-10T08:30:00Z" };
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("profile")) return Promise.resolve({ status: 404, ok: false });
      if (options?.method === "DELETE") return Promise.resolve({ ok: true });
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [record], total: 1, latest: record }) });
    });
    const user = userEvent.setup();
    renderPage(fetchMock);

    await screen.findAllByText("70.00 kg");
    await user.click(screen.getByRole("button", { name: "Delete" }));

    expect(await screen.findByText("Weight record deleted.")).toBeInTheDocument();
    expect(screen.getByText("No weight records yet. Add your first measurement above.")).toBeInTheDocument();
  });
});
