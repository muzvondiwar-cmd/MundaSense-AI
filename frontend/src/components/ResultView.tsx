import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  ClipboardCheck,
  Info,
  MapPin,
  ShieldAlert,
  Sprout,
} from "lucide-react";
import type { ReactNode } from "react";

import type { AssessmentResponse } from "../types/api";
import { PageHeader, SectionHeader } from "./PageHeader";
import { ConfidenceBadge, RiskBadge } from "./RiskBadge";
import { Alert, Badge, Card } from "./ui";

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function IntervalBar({ result }: { result: AssessmentResponse }) {
  const low = result.prediction.range_low_t_ha;
  const high = result.prediction.range_high_t_ha;
  const estimate = result.prediction.yield_t_ha;
  const max = Math.max(high * 1.08, 1);
  const left = (low / max) * 100;
  const width = Math.max(((high - low) / max) * 100, 2);
  const point = (estimate / max) * 100;
  return (
    <div
      className="mt-6"
      role="img"
      aria-label={`Predicted yield ${estimate.toFixed(2)} tonnes per hectare with a plausible range from ${low.toFixed(2)} to ${high.toFixed(2)}.`}
    >
      <div className="relative h-3 rounded-full bg-green-100">
        <div
          className="absolute top-0 h-3 rounded-full bg-teal/35"
          style={{ left: `${left}%`, width: `${width}%` }}
        />
        <span
          className="absolute top-1/2 size-5 -translate-x-1/2 -translate-y-1/2 rounded-full border-4 border-white bg-deep shadow"
          style={{ left: `${point}%` }}
        />
      </div>
      <div className="mt-2 flex justify-between text-xs font-semibold text-muted">
        <span>{low.toFixed(2)} t/ha</span>
        <span>Estimate {estimate.toFixed(2)}</span>
        <span>{high.toFixed(2)} t/ha</span>
      </div>
    </div>
  );
}

function RiskGauge({ score }: { score: number }) {
  const color = score >= 70 ? "#CF1737" : score >= 40 ? "#E0A000" : "#078B8B";
  return (
    <div className="grid place-items-center">
      <div
        className="grid size-36 place-items-center rounded-full"
        style={{
          background: `conic-gradient(${color} ${score * 3.6}deg, color-mix(in srgb, ${color} 14%, transparent) 0)`,
        }}
        role="img"
        aria-label={`Risk score ${score} out of 100`}
      >
        <div className="grid size-28 place-items-center rounded-full bg-white text-center shadow-inner">
          <div>
            <p className="text-4xl font-black text-ink">{score.toFixed(0)}</p>
            <p className="text-xs font-bold uppercase text-muted">
              of 100 risk
            </p>
          </div>
        </div>
      </div>
      <p className="mt-3 max-w-48 text-center text-xs leading-5 text-muted">
        A transparent concern scale derived from provisional yield
        thresholds—not a probability.
      </p>
    </div>
  );
}

function InputProfile({ result }: { result: AssessmentResponse }) {
  const items = [
    ["Rainfall", result.inputs.rainfall.value, 650, "mm"],
    ["Fertiliser", result.inputs.fertilizer.value, 120, "kg/ha"],
    ["Temperature", result.inputs.temperature.value, 24, "°C"],
    ["Humidity", result.inputs.humidity.value, 62, "%"],
    ["Soil pH", result.inputs.soil_ph.value, 6.2, "pH"],
  ] as const;
  return (
    <Card className="p-5">
      <h3 className="font-extrabold text-ink">Input profile</h3>
      <p className="mt-1 text-sm text-muted">
        Recorded value compared with a demonstration reference—not an agronomic
        target.
      </p>
      <div className="mt-5 grid gap-4">
        {items.map(([label, value, reference, unit]) => {
          const position = Math.min(
            100,
            Math.max(4, (value / (reference * 2)) * 100),
          );
          return (
            <div key={label}>
              <div className="flex justify-between gap-3 text-xs">
                <span className="font-bold text-ink">{label}</span>
                <span className="text-muted">
                  {value.toLocaleString()} {unit} · ref {reference}
                </span>
              </div>
              <div className="relative mt-2 h-2 rounded-full bg-pale">
                <span
                  className="absolute left-1/2 top-[-3px] h-4 w-px bg-gold"
                  aria-hidden="true"
                />
                <span
                  className="absolute top-0 h-2 rounded-full bg-teal"
                  style={{ width: `${position}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function DriverBars({ result }: { result: AssessmentResponse }) {
  const max = Math.max(...result.drivers.map((item) => item.importance), 0.01);
  return (
    <div className="grid gap-3">
      {result.drivers.map((driver, index) => {
        const Icon =
          driver.direction === "raises_yield"
            ? ArrowUpRight
            : driver.direction === "lowers_yield"
              ? ArrowDownRight
              : ArrowRight;
        const direction =
          driver.direction === "raises_yield"
            ? "supported the estimate"
            : driver.direction === "lowers_yield"
              ? "pushed the estimate lower"
              : "had little relative effect";
        const positive = driver.direction === "raises_yield";
        const width = Math.max((driver.importance / max) * 48, 4);
        return (
          <Card key={driver.feature} className="p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-muted">
                  Driver {index + 1}
                </p>
                <h3 className="mt-1 font-extrabold text-ink">{driver.label}</h3>
              </div>
              <Badge
                tone={
                  positive
                    ? "green"
                    : driver.direction === "neutral"
                      ? "neutral"
                      : "gold"
                }
              >
                <Icon className="size-3.5" />
                {direction}
              </Badge>
            </div>
            <div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center">
              <div className="flex justify-end">
                <div
                  className={`h-2 rounded-l-full ${positive ? "bg-green-100" : "bg-gold"}`}
                  style={{ width: positive ? "0" : `${width}%` }}
                />
              </div>
              <span className="h-5 w-px bg-slate-400" />
              <div>
                <div
                  className={`h-2 rounded-r-full ${positive ? "bg-teal" : "bg-amber-100"}`}
                  style={{ width: positive ? `${width}%` : "0" }}
                />
              </div>
            </div>
            <p className="mt-3 text-sm font-semibold text-ink">
              {driver.value.toLocaleString()} {driver.unit}
            </p>
            <p className="mt-1 text-sm leading-6 text-muted">
              {driver.explanation}
            </p>
          </Card>
        );
      })}
    </div>
  );
}

export function ResultView({
  result,
  title = "Your maize risk picture",
  actions,
}: {
  result: AssessmentResponse;
  title?: string;
  actions?: ReactNode;
}) {
  const lowConfidence =
    result.prediction.confidence.band === "low" ||
    result.prediction.confidence.band === "insufficient";
  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Explainable field result"
        title={title}
        body="Read the uncertainty and data-quality notes before considering the guarded next step."
        actions={actions}
      />
      {result.data_status === "synthetic_demo" && (
        <Alert tone="warning" title="Synthetic demo data">
          This saved result came from a demonstration or simulation preset. It
          must not be mixed invisibly with observed farm records.
        </Alert>
      )}
      {(lowConfidence ||
        result.warnings.some((item) => item.severity === "critical")) && (
        <div className="mt-4">
          <Alert tone="critical" title="Caution before action">
            This result has weak or unfamiliar model evidence. Verify
            measurements and use field inspection or extension support before
            changing management.
          </Alert>
        </div>
      )}

      <Card className="adaptive-gradient-card field-texture mt-5 overflow-hidden bg-gradient-to-br from-white to-green-50 p-5 sm:p-7">
        <div className="flex flex-wrap items-center gap-2">
          <RiskBadge
            risk={result.prediction.risk_band}
            label={result.prediction.risk_label}
          />
          <ConfidenceBadge confidence={result.prediction.confidence.band} />
          <Badge
            tone={result.data_status === "synthetic_demo" ? "gold" : "green"}
          >
            {result.data_status === "synthetic_demo"
              ? "Synthetic demo"
              : "Real assessment"}
          </Badge>
        </div>
        <div className="mt-6 grid gap-6 lg:grid-cols-[1.15fr_.55fr_.7fr]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[.12em] text-teal">
              Predicted maize yield
            </p>
            <p className="mt-2 text-5xl font-black tracking-tight text-ink sm:text-6xl">
              {result.prediction.yield_t_ha.toFixed(2)}{" "}
              <span className="text-2xl font-bold text-muted">t/ha</span>
            </p>
            <p className="mt-3 max-w-xl leading-7 text-muted">
              Plausible model range{" "}
              {result.prediction.range_low_t_ha.toFixed(2)}–
              {result.prediction.range_high_t_ha.toFixed(2)} t/ha. This is a
              calibrated range, not a guarantee.
            </p>
            <IntervalBar result={result} />
            <div className="mt-4 rounded-xl border border-line bg-white/80 p-3 text-sm">
              <strong className="text-ink">Demonstration benchmark:</strong>{" "}
              <span className="text-muted">
                3.00 t/ha is the provisional low/moderate threshold, not a local
                production target.
              </span>
            </div>
          </div>
          <RiskGauge score={result.prediction.risk_score} />
          <div className="grid content-start gap-3 rounded-2xl border border-green-200 bg-white/80 p-4">
            <div className="flex gap-3">
              <CalendarDays className="mt-0.5 size-5 text-teal" />
              <div>
                <p className="text-xs font-bold uppercase text-muted">
                  Created
                </p>
                <p className="font-semibold text-ink">
                  {formatDate(result.created_at)}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <ClipboardCheck className="mt-0.5 size-5 text-teal" />
              <div>
                <p className="text-xs font-bold uppercase text-muted">
                  Assessment ID
                </p>
                <p className="break-all font-mono text-sm text-ink">
                  {result.assessment_id}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <MapPin className="mt-0.5 size-5 text-teal" />
              <div>
                <p className="text-xs font-bold uppercase text-muted">
                  Coarse location
                </p>
                <p className="font-semibold text-ink">
                  {result.context.district || "Not recorded"}
                </p>
              </div>
            </div>
            <div className="border-t border-line pt-3">
              <p className="text-xs font-bold uppercase text-muted">
                Confidence meaning
              </p>
              <p className="mt-1 text-sm leading-6 text-ink">
                {result.prediction.confidence.method}
              </p>
            </div>
          </div>
        </div>
      </Card>

      <SectionHeader
        title="What influenced this result?"
        body="These are approximate model associations relative to demonstration reference values; influence does not prove agronomic causation."
      />
      <DriverBars result={result} />
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Card className="border-l-4 border-l-teal p-5">
          <h3 className="font-extrabold text-ink">
            Factors supporting the crop
          </h3>
          <ul className="mt-3 grid gap-2 text-sm text-muted">
            {result.drivers
              .filter((item) => item.direction === "raises_yield")
              .map((item) => (
                <li key={item.feature}>
                  • {item.label}: {item.explanation}
                </li>
              ))}
            {!result.drivers.some(
              (item) => item.direction === "raises_yield",
            ) && (
              <li>
                No top-three driver was classified as supporting the estimate.
              </li>
            )}
          </ul>
        </Card>
        <Card className="border-l-4 border-l-gold p-5">
          <h3 className="font-extrabold text-ink">
            Factors lowering expected yield
          </h3>
          <ul className="mt-3 grid gap-2 text-sm text-muted">
            {result.drivers
              .filter((item) => item.direction === "lowers_yield")
              .map((item) => (
                <li key={item.feature}>
                  • {item.label}: {item.explanation}
                </li>
              ))}
            {!result.drivers.some(
              (item) => item.direction === "lowers_yield",
            ) && (
              <li>
                No top-three driver was classified as lowering the estimate.
              </li>
            )}
          </ul>
        </Card>
      </div>

      <SectionHeader
        title="Recorded input profile"
        body="This compact comparison helps spot large departures before acting on the estimate."
      />
      <InputProfile result={result} />

      <SectionHeader
        title="Warnings and data quality"
        body="Unusual but technically processable values can continue with lower confidence; invalid values are blocked before inference."
      />
      {result.warnings.length ? (
        <div className="grid gap-3">
          {result.warnings.map((warning) => (
            <Alert
              key={warning.code}
              tone={warning.severity}
              title={warning.title}
            >
              {warning.message}
            </Alert>
          ))}
        </div>
      ) : (
        <Alert tone="success" title="No unusual-input warnings">
          All five values were within the model's configured familiar ranges for
          this release.
        </Alert>
      )}

      <SectionHeader
        title="Priority action"
        body="Selected by the versioned deterministic advisory rules—not generated by a language model."
      />
      <Card className="border-l-4 border-l-teal p-5 sm:p-6">
        <div className="flex gap-4">
          <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-teal/10 text-teal">
            <Sprout className="size-6" />
          </div>
          <div>
            <h3 className="text-xl font-extrabold text-ink">
              {result.advisory.priority_action}
            </h3>
            <p className="mt-2 leading-7 text-slate-700">
              {result.advisory.message}
            </p>
            <p className="mt-3 text-sm text-muted">
              <strong>Why this action:</strong> {result.advisory.reason}
            </p>
            {result.advisory.referral_required && (
              <div className="mt-4">
                <Alert tone="critical" title="Extension review recommended">
                  {result.advisory.referral_message}
                </Alert>
              </div>
            )}
          </div>
        </div>
      </Card>
      <div className="mt-4">
        <Alert tone="warning">
          <strong>Decision support only.</strong> {result.disclaimer}
        </Alert>
      </div>

      <details className="mt-6 rounded-xl border border-line bg-white p-4">
        <summary className="flex min-h-11 cursor-pointer items-center gap-2 font-bold text-ink">
          <Info className="size-5 text-teal" />
          How was this calculated?
        </summary>
        <p className="mt-4 text-sm leading-6 text-muted">
          The five validated numeric inputs were passed through the versioned
          local scikit-learn pipeline. The range uses held-out synthetic
          residual calibration, confidence combines range width and input
          familiarity, and drivers are approximate local model associations.
          None of these establish causation.
        </p>
        <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="text-muted">Model</p>
            <p className="font-semibold text-ink">{result.versions.model}</p>
          </div>
          <div>
            <p className="text-muted">Rules</p>
            <p className="font-semibold text-ink">{result.versions.rules}</p>
          </div>
          <div>
            <p className="text-muted">Risk policy</p>
            <p className="font-semibold text-ink">
              {result.versions.risk_policy}
            </p>
          </div>
          <div>
            <p className="text-muted">Explanation</p>
            <p className="font-semibold text-ink">
              {result.explanation_method}
            </p>
          </div>
        </div>
        <p className="mt-4 text-sm leading-6 text-muted">
          <ShieldAlert className="mr-2 inline size-4" />
          The bundled model is trained only on synthetic data and is not
          field-validated.
        </p>
      </details>
    </div>
  );
}
