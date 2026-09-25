import { describe, expect, it } from "vitest";

import {
  assessmentSchema,
  defaultAssessment,
  normalizeOptionalNumber,
} from "../features/assessment/schema";

describe("assessmentSchema", () => {
  it("accepts the complete five-input maize contract", () => {
    const result = assessmentSchema.safeParse(defaultAssessment);
    expect(result.success).toBe(true);
  });

  it("rejects a field outside the hard processing limits", () => {
    const result = assessmentSchema.safeParse({
      ...defaultAssessment,
      rainfall_mm: -1,
    });
    expect(result.success).toBe(false);
    if (!result.success)
      expect(result.error.issues[0].path).toEqual(["rainfall_mm"]);
  });

  it("keeps an empty optional field size null instead of coercing it to zero", () => {
    expect(normalizeOptionalNumber(null)).toBeNull();
    expect(normalizeOptionalNumber("")).toBeNull();
    expect(normalizeOptionalNumber("1.25")).toBe(1.25);
  });
});
