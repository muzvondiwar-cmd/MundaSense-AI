import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConfidenceBadge, RiskBadge } from "../components/RiskBadge";

describe("risk and confidence badges", () => {
  it("communicates high risk with words as well as an icon", () => {
    const { container } = render(<RiskBadge risk="high" />);
    expect(screen.getByText("High yield risk")).toBeVisible();
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("renders insufficient confidence explicitly", () => {
    render(<ConfidenceBadge confidence="insufficient" />);
    expect(screen.getByText("Insufficient basis")).toBeVisible();
  });
});
