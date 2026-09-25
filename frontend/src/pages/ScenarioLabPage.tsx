import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowRight, Beaker, Clipboard, RotateCcw, Save, TriangleAlert } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { usePreferences } from "../app/Preferences";
import { PageHeader, SectionHeader } from "../components/PageHeader";
import { ConfidenceBadge, RiskBadge } from "../components/RiskBadge";
import { SimulationNotice } from "../components/SimulationNotice";
import { useToast } from "../components/Toast";
import { Alert, Badge, Button, Card, EmptyState, PageSkeleton, Spinner } from "../components/ui";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { api, assessmentToCreate } from "../services/api";
import type { AssessmentResponse, FeatureConfig } from "../types/api";

function inputsOf(result: AssessmentResponse) {
  return { rainfall_mm: result.inputs.rainfall.value, fertilizer_kg_ha: result.inputs.fertilizer.value, temperature_c: result.inputs.temperature.value, humidity_pct: result.inputs.humidity.value, soil_ph: result.inputs.soil_ph.value };
}

export default function ScenarioLabPage() {
  const [params, setParams] = useSearchParams();
  const baselineId = params.get("baseline") ?? "";
  const [values, setValues] = useState<Record<string, number>>({});
  const saving = useRef(false);
  const debounced = useDebouncedValue(values, 500);
  const { locale } = usePreferences();
  const { notify } = useToast();
  const navigate = useNavigate();
  const history = useQuery({ queryKey: ["history", "scenario-select"], queryFn: () => api.listAssessments("") });
  const config = useQuery({ queryKey: ["config", locale], queryFn: () => api.config(locale) });
  const baseline = useQuery({ queryKey: ["assessment", baselineId, locale], queryFn: () => api.getAssessment(baselineId, locale), enabled: Boolean(baselineId) });
  useEffect(() => { if (!baselineId && history.data?.items[0]) setParams({ baseline: history.data.items[0].assessment_id }, { replace: true }); }, [baselineId, history.data, setParams]);
  useEffect(() => { if (baseline.data) setValues(inputsOf(baseline.data)); }, [baseline.data]);
  const simulation = useQuery({ queryKey: ["scenario", baselineId, debounced, locale], queryFn: () => api.simulate(baselineId, debounced, locale), enabled: Boolean(baseline.data && Object.keys(debounced).length === 5), staleTime: 0, retry: false });
  const save = useMutation({ mutationFn: async () => { if (!simulation.data) throw new Error("No scenario to save"); const payload = assessmentToCreate(simulation.data.scenario); return api.createAssessment({ ...payload, source: "scenario", farm_reference: `${baseline.data?.context.farm_reference || "Field"} · scenario` }); }, onSuccess: (result) => { notify("Scenario saved as a new labelled assessment"); navigate(`/assess/${result.assessment_id}/result`); }, onSettled: () => { saving.current = false; } });
  const features = useMemo(() => Object.fromEntries((config.data?.features ?? []).map((item) => [item.key, item])) as Record<string, FeatureConfig>, [config.data]);
  if (history.isLoading || config.isLoading) return <PageSkeleton />;
  if (!history.data?.items.length) return <EmptyState icon={<Beaker className="size-6" />} title="A baseline is required" body="Run and save a maize assessment before exploring a what-if simulation." action={<Link className="button button-primary" to="/assess/new">Start assessment</Link>} />;

  const compared = simulation.data;
  const chartData = compared ? [{ name: "Baseline", estimate: compared.baseline.prediction.yield_t_ha, low: compared.baseline.prediction.range_low_t_ha, high: compared.baseline.prediction.range_high_t_ha }, { name: "Scenario", estimate: compared.scenario.prediction.yield_t_ha, low: compared.scenario.prediction.range_low_t_ha, high: compared.scenario.prediction.range_high_t_ha }] : [];

  return <div className="page-enter">
    <PageHeader eyebrow="Responsible what-if exploration" title="Climate Scenario Lab" body="Compare one saved baseline with adjusted values using the same local Python prediction pipeline." />
    <SimulationNotice />
    <div className="mt-5 grid gap-5 xl:grid-cols-[.9fr_1.1fr]">
      <Card className="p-5"><label className="label" htmlFor="baseline">Baseline assessment</label><select id="baseline" className="input" value={baselineId} onChange={(event) => setParams({ baseline: event.target.value })}>{history.data.items.map((item) => <option key={item.assessment_id} value={item.assessment_id}>{item.farm_reference || item.assessment_id.slice(0, 8)} · {item.risk_band} risk · {new Date(item.created_at).toLocaleDateString()}</option>)}</select>{baseline.isLoading ? <div className="mt-5"><Spinner label="Loading immutable baseline" /></div> : baseline.data && <div className="mt-5 rounded-xl border border-line bg-pale p-4"><div className="flex flex-wrap gap-2"><RiskBadge risk={baseline.data.prediction.risk_band} /><ConfidenceBadge confidence={baseline.data.prediction.confidence.band} /></div><p className="mt-4 text-4xl font-black text-ink">{baseline.data.prediction.yield_t_ha.toFixed(2)} <span className="text-lg text-muted">t/ha</span></p><p className="mt-1 text-sm text-muted">{baseline.data.context.farm_reference || "Unnamed field"} · {baseline.data.context.district || "No district"}</p></div>}</Card>
      <Card className="p-5"><div className="flex items-start justify-between gap-3"><div><h2 className="text-xl font-extrabold text-ink">Scenario inputs</h2><p className="mt-1 text-sm text-muted">Each slider is paired with a precise numeric field.</p></div>{simulation.isFetching && <Badge tone="teal"><Spinner label="Updating" /></Badge>}</div><div className="mt-5 grid gap-5">{Object.values(features).map((feature) => <div key={feature.key}><div className="flex items-end justify-between gap-3"><label className="label" htmlFor={`${feature.key}-number`}>{feature.label} <span className="font-normal text-muted">({feature.unit})</span></label><input id={`${feature.key}-number`} className="input w-28 py-1.5" type="number" value={values[feature.key] ?? ""} min={feature.hard_min} max={feature.hard_max} step={feature.key === "soil_ph" ? .1 : 1} onChange={(event) => setValues((current) => ({ ...current, [feature.key]: Number(event.target.value) }))} /></div><input aria-label={`${feature.label} slider`} className="w-full accent-deep" type="range" value={values[feature.key] ?? feature.example} min={feature.hard_min} max={feature.hard_max} step={feature.key === "soil_ph" ? .1 : 1} onChange={(event) => setValues((current) => ({ ...current, [feature.key]: Number(event.target.value) }))} /></div>)}</div><div className="mt-5 flex flex-wrap gap-2"><Button variant="secondary" onClick={() => baseline.data && setValues(inputsOf(baseline.data))}><RotateCcw className="size-4" />Reset to baseline</Button><Button variant="secondary" onClick={async () => { await navigator.clipboard.writeText(JSON.stringify(values, null, 2)); notify("Scenario values copied"); }}><Clipboard className="size-4" />Copy values</Button><Button disabled={!compared || save.isPending} onClick={() => { if (saving.current) return; saving.current = true; save.mutate(); }}><Save className="size-4" />Save as new assessment</Button></div></Card>
    </div>

    {simulation.isError && <div className="mt-5"><Alert tone="critical" title="Scenario could not be processed">One or more values may be outside hard technical limits, or the backend is unavailable. The baseline remains unchanged.</Alert></div>}
    {compared && <><SectionHeader title="Baseline versus scenario" body="Read the side-by-side values as well as the chart; the chart is not required to understand the comparison." />{compared.scenario.warnings.length > 0 && <Alert tone={compared.scenario.warnings.some((item) => item.severity === "critical") ? "critical" : "warning"} title="Scenario has unfamiliar inputs">{compared.scenario.warnings[0].message} Review all warnings before interpreting the projected change.</Alert>}<div className="mt-4 grid gap-5 lg:grid-cols-[1fr_1.1fr]"><Card className="p-5"><div className="grid gap-4 sm:grid-cols-2"><div><Badge tone="neutral">Baseline</Badge><p className="mt-3 text-4xl font-black text-ink">{compared.baseline.prediction.yield_t_ha.toFixed(2)} <span className="text-base text-muted">t/ha</span></p><div className="mt-3 flex flex-wrap gap-2"><RiskBadge risk={compared.baseline.prediction.risk_band} /><ConfidenceBadge confidence={compared.baseline.prediction.confidence.band} /></div></div><div><Badge tone="teal">Scenario</Badge><p className="mt-3 text-4xl font-black text-ink">{compared.scenario.prediction.yield_t_ha.toFixed(2)} <span className="text-base text-muted">t/ha</span></p><div className="mt-3 flex flex-wrap gap-2"><RiskBadge risk={compared.scenario.prediction.risk_band} /><ConfidenceBadge confidence={compared.scenario.prediction.confidence.band} /></div></div></div><div className="mt-5 flex items-center gap-3 rounded-xl bg-pale p-4"><ArrowRight className="size-5 text-teal" /><p><strong>{compared.delta.yield_t_ha >= 0 ? "+" : ""}{compared.delta.yield_t_ha.toFixed(2)} t/ha</strong> change in central estimate. This is a model response, not a promised outcome.</p></div></Card><Card className="min-h-80 p-4"><div className="h-72" role="img" aria-label={`Bar chart comparing baseline yield ${compared.baseline.prediction.yield_t_ha.toFixed(2)} with scenario yield ${compared.scenario.prediction.yield_t_ha.toFixed(2)} tonnes per hectare.`}><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} margin={{ top: 15, right: 15, left: 0, bottom: 5 }}><CartesianGrid strokeDasharray="3 3" stroke="#dce9dd" /><XAxis dataKey="name" /><YAxis unit=" t/ha" /><Tooltip /><Legend /><Bar dataKey="estimate" name="Central estimate" fill="#1b5e20" radius={[8,8,0,0]} /><Bar dataKey="low" name="Range low" fill="#d99a00" radius={[8,8,0,0]} /><Bar dataKey="high" name="Range high" fill="#00796b" radius={[8,8,0,0]} /></BarChart></ResponsiveContainer></div></Card></div></>}
  </div>;
}
