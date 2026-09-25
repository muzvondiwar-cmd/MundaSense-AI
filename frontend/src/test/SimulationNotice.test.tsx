import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SimulationNotice } from "../components/SimulationNotice";

describe("Scenario Lab safeguard", () => {
  it("states that simulations are neither forecasts nor prescriptions", () => {
    render(<SimulationNotice />);
    expect(screen.getByText(/Simulation only/)).toBeVisible();
    expect(screen.getByText(/not saved automatically/i)).toBeVisible();
    expect(screen.getByText(/recommended fertiliser rate/i)).toBeVisible();
  });
});
