import { describe, expect, it } from "vitest";

import { translate } from "../i18n/translations";

describe("translation fallback", () => {
  it("uses reviewed Shona where it exists", () => {
    expect(translate("sn", "nav.home")).toBe("Kumba");
  });

  it("falls back to English for an unreviewed Shona key", () => {
    expect(translate("sn", "nav.dashboard")).toBe("Officer dashboard");
  });
});
