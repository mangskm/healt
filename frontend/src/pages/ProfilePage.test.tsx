import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProfilePage } from "./ProfilePage";

describe("ProfilePage", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("creates a profile from the form", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ status: 404, ok: false })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({
        id: "00000000-0000-0000-0000-000000000001", preferred_name: "Mali", date_of_birth: null,
        sex: null, height_cm: null, weight_unit: "kg", height_unit: "cm", timezone: "Asia/Bangkok",
        created_at: "2026-09-06T00:00:00Z", updated_at: "2026-09-06T00:00:00Z",
      }) });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<BrowserRouter><ProfilePage /></BrowserRouter>);
    await user.type(await screen.findByLabelText("Display name"), "Mali");
    await user.click(screen.getByRole("button", { name: "Save profile" }));
    expect(await screen.findByText("Profile saved.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining("/api/v1/profile"), expect.objectContaining({ method: "PATCH" }));
  });
});
