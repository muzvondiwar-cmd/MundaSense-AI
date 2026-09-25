import { Alert } from "./ui";

export function SimulationNotice() {
  return <Alert tone="warning" title="Simulation only — not a weather forecast or input prescription">Changes are not saved automatically. A higher simulated estimate does not establish an optimal input or recommended fertiliser rate.</Alert>;
}
