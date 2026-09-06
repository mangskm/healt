export type Sex = "female" | "male" | "intersex" | "prefer_not_to_say";
export type WeightUnit = "kg" | "lb";
export type HeightUnit = "cm" | "ft_in";

export interface Profile {
  id: string;
  preferred_name: string | null;
  date_of_birth: string | null;
  sex: Sex | null;
  height_cm: number | null;
  weight_unit: WeightUnit | null;
  height_unit: HeightUnit | null;
  timezone: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdate {
  preferred_name?: string | null;
  date_of_birth?: string | null;
  sex?: Sex | null;
  height_cm?: number | null;
  weight_unit?: WeightUnit | null;
  height_unit?: HeightUnit | null;
  timezone?: string | null;
}
