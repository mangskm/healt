import type { DistanceUnit } from "../types/exercise";

const KM_PER_MILE = 1.609344;

export function convertDistance(value: number, from: DistanceUnit, to: DistanceUnit): number {
  if (from === to) return value;
  return from === "mi" ? value * KM_PER_MILE : value / KM_PER_MILE;
}

export function formatDistance(kilometers: number, unit: DistanceUnit): string {
  return `${convertDistance(kilometers, "km", unit).toFixed(2)} ${unit}`;
}
