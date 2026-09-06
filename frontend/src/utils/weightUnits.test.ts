import { describe, expect, it } from "vitest";

import { convertWeight, formatWeight } from "./weightUnits";

describe("weight unit conversion", () => {
  it("converts pounds and kilograms using the shared conversion", () => {
    expect(convertWeight(150, "lb", "kg")).toBe(68.04);
    expect(convertWeight(68.039, "kg", "lb")).toBe(150);
  });

  it("formats a canonical kilogram value in the selected unit", () => {
    expect(formatWeight(70, "lb")).toBe("154.32 lb");
  });
});
