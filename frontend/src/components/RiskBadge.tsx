import { AlertTriangle, CheckCircle2, CircleAlert, ShieldQuestion } from "lucide-react";

import type { ConfidenceBand, RiskBand } from "../types/api";
import { Badge } from "./ui";

export function RiskBadge({ risk, label }: { risk: RiskBand; label?: string }) {
  const config = {
    low: { tone: "green" as const, Icon: CheckCircle2, text: "Low yield risk" },
    moderate: { tone: "gold" as const, Icon: CircleAlert, text: "Moderate yield risk" },
    high: { tone: "red" as const, Icon: AlertTriangle, text: "High yield risk" },
  }[risk];
  return <Badge tone={config.tone}><config.Icon className="size-3.5" aria-hidden="true" />{label ?? config.text}</Badge>;
}

export function ConfidenceBadge({ confidence }: { confidence: ConfidenceBand }) {
  const risky = confidence === "low" || confidence === "insufficient";
  return <Badge tone={risky ? "red" : confidence === "medium" ? "gold" : "teal"}><ShieldQuestion className="size-3.5" aria-hidden="true" />{confidence === "insufficient" ? "Insufficient basis" : `${confidence[0].toUpperCase()}${confidence.slice(1)} confidence`}</Badge>;
}
