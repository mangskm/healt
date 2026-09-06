import type { WeightUnit } from "./profile";

export interface WeightRecord {
  id: string;
  weight_kg: number;
  recorded_at: string;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface WeightRecordList {
  items: WeightRecord[];
  total: number;
  latest: WeightRecord | null;
}

export interface WeightRecordInput {
  weight: number;
  unit: WeightUnit;
  recorded_at: string;
  note?: string | null;
}

export type WeightRecordUpdate = Partial<WeightRecordInput>;
