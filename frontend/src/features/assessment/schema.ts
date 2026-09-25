import { z } from "zod";

export const assessmentSchema = z.object({
  crop: z.literal("maize"),
  rainfall_mm: z.coerce.number().min(0, "Rainfall cannot be below 0 mm.").max(2000, "Rainfall cannot exceed 2,000 mm."),
  fertilizer_kg_ha: z.coerce.number().min(0, "Recorded fertiliser cannot be negative.").max(1000, "Recorded fertiliser cannot exceed 1,000 kg/ha."),
  temperature_c: z.coerce.number().min(-10, "Temperature cannot be below -10 °C.").max(60, "Temperature cannot exceed 60 °C."),
  humidity_pct: z.coerce.number().min(0, "Humidity cannot be below 0%.").max(100, "Humidity cannot exceed 100%."),
  soil_ph: z.coerce.number().min(0, "Soil pH cannot be below 0.").max(14, "Soil pH cannot exceed 14."),
  season: z.string().max(30, "Season must be 30 characters or fewer."),
  district: z.string().max(80, "District must be 80 characters or fewer."),
  farm_reference: z.string().max(80, "Field alias must be 80 characters or fewer."),
  language: z.enum(["en", "sn"]),
  source: z.enum(["manual", "demo", "scenario"]),
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
};
