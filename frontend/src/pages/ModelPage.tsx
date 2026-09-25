import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BarChart3, Database, FlaskConical, Gauge, ShieldCheck } from "lucide-react";

import { usePreferences } from "../app/Preferences";
import { PageHeader, SectionHeader } from "../components/PageHeader";
import { Alert, Badge, Card, PageSkeleton } from "../components/ui";
import { api } from "../services/api";

export default function ModelPage() {
  const { locale } = usePreferences();
  const model = useQuery({ queryKey: ["model-card", locale], queryFn: () => api.modelCard(locale) });
  if (model.isLoading) return <PageSkeleton />;
  if (!model.data) return <Alert tone="critical" title="Model metadata unavailable">The local model registry could not be read.</Alert>;
  const data = model.data;
  return <div className="page-enter">
    <PageHeader eyebrow="Transparent model evidence" title="Model card" body="Release metadata, synthetic held-out metrics, feature contracts, and limitations for the exact local model bundle." />
    <Alert tone="warning" title={data.status}>These values test the software and synthetic pipeline. They do not establish farmer impact, agronomic efficacy, or field accuracy.</Alert>
    <div className="mt-5 grid gap-4 md:grid-cols-3"><Card className="p-5"><Database className="size-6 text-teal" /><p className="mt-4 text-xs font-bold uppercase tracking-wider text-muted">Model version</p><p className="mt-1 font-extrabold text-ink">{data.model_version}</p></Card><Card className="p-5"><BarChart3 className="size-6 text-teal" /><p className="mt-4 text-xs font-bold uppercase tracking-wider text-muted">Champion</p><p className="mt-1 font-extrabold text-ink">{data.champion}</p></Card><Card className="p-5"><FlaskConical className="size-6 text-teal" /><p className="mt-4 text-xs font-bold uppercase tracking-wider text-muted">Created</p><p className="mt-1 font-extrabold text-ink">{new Date(data.created_at).toLocaleString()}</p></Card></div>
    <SectionHeader title="Held-out synthetic metrics" body="Displayed with their units and limitations; no real-world performance claim is implied." />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{data.metrics.map((metric) => <Card key={metric.label} className="p-5"><p className="text-xs font-bold uppercase tracking-wider text-muted">{metric.label}</p><p className="mt-2 text-3xl font-black text-ink">{metric.unit === "proportion" ? `${(metric.value * 100).toFixed(1)}%` : metric.value.toFixed(3)} {metric.unit && metric.unit !== "proportion" ? <span className="text-sm text-muted">{metric.unit}</span> : null}</p></Card>)}</div>
    <SectionHeader title="Five-feature contract" body="Hard limits block technically invalid values; fitted training ranges may trigger warnings at narrower boundaries." />
    <div className="overflow-hidden rounded-2xl border border-line bg-white"><table className="w-full text-left text-sm"><thead className="bg-pale text-xs uppercase tracking-wider text-muted"><tr><th className="p-3">Feature</th><th className="p-3">Unit</th><th className="p-3">Hard range</th><th className="p-3">Demo reference</th></tr></thead><tbody>{data.features.map((feature) => <tr key={feature.key} className="border-t border-line"><td className="p-3 font-bold text-ink">{feature.label}</td><td className="p-3">{feature.unit}</td><td className="p-3">{feature.hard_min}–{feature.hard_max}</td><td className="p-3">{feature.example}</td></tr>)}</tbody></table></div>
    <SectionHeader title="Methods and limitations" />
    <div className="grid gap-4 lg:grid-cols-[.8fr_1.2fr]"><Card className="p-5"><div className="flex items-center gap-3"><Gauge className="size-6 text-teal" /><h3 className="text-xl font-extrabold text-ink">How results are built</h3></div><dl className="mt-5 grid gap-4 text-sm"><div><dt className="font-bold text-muted">Explanation</dt><dd className="mt-1 text-ink">{data.explanation_method}</dd></div><div><dt className="font-bold text-muted">Plausible range</dt><dd className="mt-1 text-ink">{data.interval_method}</dd></div></dl></Card><Card className="p-5"><div className="flex items-center gap-3"><AlertTriangle className="size-6 text-gold" /><h3 className="text-xl font-extrabold text-ink">Known limitations</h3></div><ul className="mt-4 grid gap-3">{data.limitations.map((item) => <li key={item} className="flex gap-3 text-sm leading-6 text-slate-700"><ShieldCheck className="mt-1 size-4 shrink-0 text-teal" />{item}</li>)}</ul></Card></div>
  </div>;
}
