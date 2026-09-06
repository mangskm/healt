import { describe, expect, it } from "vitest";
import { convertDistance } from "./distanceUnits";

describe("convertDistance", () => {
  it("converts miles and kilometers consistently", () => {
    expect(convertDistance(3, "mi", "km")).toBeCloseTo(4.828032);
    expect(convertDistance(4.828032, "km", "mi")).toBeCloseTo(3);
  });
});
