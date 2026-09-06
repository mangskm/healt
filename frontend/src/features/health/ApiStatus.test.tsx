import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiStatus } from "./ApiStatus";

describe("ApiStatus", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("shows a successful API connection", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok", database: "connected" }),
      }),
    );

    render(<ApiStatus />);

    expect(await screen.findByText("API connected · Database connected")).toBeInTheDocument();
  });
});
