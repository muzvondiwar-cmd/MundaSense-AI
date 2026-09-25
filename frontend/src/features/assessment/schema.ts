import { z } from "zod";

export function normalizeOptionalNumber(value: unknown): number | null {
  return value === "" || value == null ? null : Number(value);
}

export const assessmentSchema = z.object({
  crop: z.literal("maize"),
  rainfall_mm: z.coerce
    .number()
    .min(0, "Rainfall cannot be below 0 mm.")
    .max(2000, "Rainfall cannot exceed 2,000 mm."),
  fertilizer_kg_ha: z.coerce
    .number()
    .min(0, "Recorded fertiliser cannot be negative.")
    .max(1000, "Recorded fertiliser cannot exceed 1,000 kg/ha."),
  temperature_c: z.coerce
    .number()
    .min(-10, "Temperature cannot be below -10 °C.")
    .max(60, "Temperature cannot exceed 60 °C."),
  humidity_pct: z.coerce
    .number()
    .min(0, "Humidity cannot be below 0%.")
    .max(100, "Humidity cannot exceed 100%."),
  soil_ph: z.coerce
    .number()
    .min(0, "Soil pH cannot be below 0.")
    .max(14, "Soil pH cannot exceed 14."),
  season: z.string().max(30, "Season must be 30 characters or fewer."),
  district: z.string().max(80, "District must be 80 characters or fewer."),
  farm_reference: z
    .string()
    .max(80, "Field alias must be 80 characters or fewer."),
  language: z.enum(["en", "sn"]),
  source: z.enum(["manual", "demo", "scenario"]),
  field_id: z.string().nullable().optional(),
  province: z.string().max(80, "Province must be 80 characters or fewer."),
  ward: z.string().max(80, "Ward must be 80 characters or fewer."),
  planting_date: z.string().nullable(),
  maize_variety: z
    .string()
    .max(100, "Maize variety must be 100 characters or fewer."),
  growth_stage: z
    .string()
    .max(80, "Growth stage must be 80 characters or fewer."),
  field_size_hectares: z
    .number()
    .positive("Field size must be above zero.")
    .max(10000)
    .nullable(),
  fertilizer_type: z
    .string()
    .max(100, "Fertiliser type must be 100 characters or fewer."),
  irrigation_available: z.boolean().nullable(),
  crop_stress_observations: z
    .string()
    .max(1000, "Observations must be 1,000 characters or fewer."),
  idempotency_key: z.string().optional(),
});

export type AssessmentFormData = z.infer<typeof assessmentSchema>;

export const defaultAssessment: AssessmentFormData = {
  crop: "maize",
  rainfall_mm: 650,
  fertilizer_kg_ha: 120,
  temperature_c: 24,
  humidity_pct: 62,
  soil_ph: 6.2,
  season: "2025/26",
  district: "",
  farm_reference: "",
  language: "en",
  source: "manual",
  field_id: null,
  province: "",
  ward: "",
  planting_date: null,
  maize_variety: "",
  growth_stage: "Vegetative",
  field_size_hectares: null,
  fertilizer_type: "",
  irrigation_available: null,
  crop_stress_observations: "",
  idempotency_key: undefined,
};
