import { useState } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ConfirmProvider, useConfirm } from "./UiProviders";

function DeletableExample() {
  const confirm = useConfirm(); const [deleted, setDeleted] = useState(false);
  return <><button type="button" onClick={() => void confirm({ title: "Delete example?", description: "This record will be removed." }).then(setDeleted)}>Delete</button>{deleted && <p>Deleted</p>}</>;
}

describe("ConfirmProvider", () => {
  it("requires an explicit confirmation before completing a destructive action", async () => {
    const user = userEvent.setup();
    render(<ConfirmProvider><DeletableExample /></ConfirmProvider>);
    await user.click(screen.getByRole("button", { name: "Delete" }));
    expect(screen.getByRole("alertdialog", { name: "Delete example?" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.queryByText("Deleted")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Delete" }));
    await user.click(screen.getAllByRole("button", { name: "Delete" })[1]);
    expect(await screen.findByText("Deleted")).toBeInTheDocument();
  });
});
