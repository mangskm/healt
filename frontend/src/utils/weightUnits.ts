import type { WeightUnit } from "../types/profile";

const KG_PER_POUND = 0.45359237;
const DISPLAY_DECIMALS = 2;

export function convertWeight(value: number, from: WeightUnit, to: WeightUnit): number {
  if (from === to) return roundForDisplay(value);
  const kilograms = from === "kg" ? value : value * KG_PER_POUND;
  return roundForDisplay(to === "kg" ? kilograms : kilograms / KG_PER_POUND);
}

export function formatWeight(weightKg: number, unit: WeightUnit): string {
  return `${convertWeight(weightKg, "kg", unit).toFixed(DISPLAY_DECIMALS)} ${unit}`;
}

function roundForDisplay(value: number): number {
  return Math.round((value + Number.EPSILON) * 10 ** DISPLAY_DECIMALS) / 10 ** DISPLAY_DECIMALS;
}
