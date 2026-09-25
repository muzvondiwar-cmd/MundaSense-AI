import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Check, ClipboardCheck, CloudSun, FlaskConical, Leaf, LoaderCircle, MapPin, ShieldAlert, Sprout } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { FormProvider, useForm, useFormContext } from "react-hook-form";
import { useNavigate, useSearchParams } from "react-router-dom";

import { usePreferences } from "../app/Preferences";
import { PageHeader } from "../components/PageHeader";
import { useToast } from "../components/Toast";
import { Alert, Badge, Button, Card, PageSkeleton, Spinner } from "../components/ui";
import { assessmentSchema, defaultAssessment, type AssessmentFormData } from "../features/assessment/schema";
import { ApiError, api } from "../services/api";
import type { FeatureConfig } from "../types/api";

const steps = [
  { title: "Field context", icon: MapPin },
  { title: "Climate observations", icon: CloudSun },
  { title: "Soil & recorded input", icon: FlaskConical },
  { title: "Review & assess", icon: ClipboardCheck },
];

function NumberField({ feature, helper }: { feature: FeatureConfig; helper: string }) {
  const { register, formState: { errors } } = useFormContext<AssessmentFormData>();
  const error = errors[feature.key]?.message;
  return <label className="block"><span className="label">{feature.label} <span className="font-normal text-muted">({feature.unit})</span></span><input type="number" step={feature.key === "soil_ph" ? "0.1" : feature.key.includes("temperature") ? "0.5" : "1"} min={feature.hard_min} max={feature.hard_max} className="input" aria-invalid={Boolean(error)} aria-describedby={`${feature.key}-help ${feature.key}-error`} {...register(feature.key)} /><span id={`${feature.key}-help`} className="help block">{helper} Hard processing limit: {feature.hard_min}–{feature.hard_max}.</span>{error && <span id={`${feature.key}-error`} className="error block">{String(error)}</span>}</label>;
}

export default function AssessmentPage() {
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState(0);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const loadedPreset = useRef(false);
  const submitting = useRef(false);
  const navigate = useNavigate();
  const { locale } = usePreferences();
  const { notify } = useToast();
  const config = useQuery({ queryKey: ["config", locale], queryFn: () => api.config(locale) });
  const scenarios = useQuery({ queryKey: ["demo-scenarios"], queryFn: api.demoScenarios });
  const methods = useForm<AssessmentFormData>({ resolver: zodResolver(assessmentSchema), defaultValues: { ...defaultAssessment, language: locale }, mode: "onTouched" });
  const { handleSubmit, reset, watch, setError, setValue, trigger, formState: { errors } } = methods;
  const values = watch();
  const mutation = useMutation({ mutationFn: api.createAssessment, onSuccess: (result) => { notify("Assessment completed and saved locally"); navigate(`/assess/${result.assessment_id}/result`); }, onError: (error) => {
    if (error instanceof ApiError) {
      const response = error.detail as { detail?: { errors?: Array<{ field?: string; message?: string }> } | Array<{ loc?: Array<string | number>; msg?: string }> };
      const detail = response?.detail;
      if (Array.isArray(detail)) {
        detail.forEach((item) => {
          const field = item.loc?.at(-1);
          if (typeof field === "string" && field in defaultAssessment) setError(field as keyof AssessmentFormData, { type: "server", message: item.msg ?? "Invalid value." });
        });
      } else {
        detail?.errors?.forEach((item) => {
          if (item.field && item.field in defaultAssessment) setError(item.field as keyof AssessmentFormData, { type: "server", message: item.message ?? "Invalid value." });
        });
      }
      setSubmitError("The local service rejected one or more values. Review the highlighted fields and try again.");
      return;
    }
    setSubmitError("The assessment could not be completed. Confirm that the local backend is ready and retry.");
  }, onSettled: () => { submitting.current = false; } });

  useEffect(() => setValue("language", locale), [locale, setValue]);
  useEffect(() => {
    const requested = searchParams.get("scenario");
    if (!requested || !scenarios.data || loadedPreset.current) return;
    const scenario = scenarios.data.find((item) => item.id === requested);
    if (scenario) {
      reset({ ...scenario.values, language: locale, source: "demo" });
      loadedPreset.current = true;
    }
  }, [locale, reset, scenarios.data, searchParams]);

  if (config.isLoading || scenarios.isLoading) return <PageSkeleton />;
  if (!config.data) return <Alert tone="critical" title="Assessment configuration unavailable">Start the local API, then retry this page.</Alert>;

  const features = Object.fromEntries(config.data.features.map((item) => [item.key, item])) as Record<string, FeatureConfig>;
  const advance = async () => {
    const fields: Array<keyof AssessmentFormData> = step === 1 ? ["rainfall_mm", "temperature_c", "humidity_pct"] : step === 2 ? ["soil_ph", "fertilizer_kg_ha"] : [];
    if (!fields.length || await trigger(fields)) setStep((current) => Math.min(current + 1, 3));
  };
  const onSubmit = (data: AssessmentFormData) => {
    if (submitting.current) return;
    submitting.current = true;
    setSubmitError(null);
    mutation.mutate(data);
  };

  return <div className="page-enter">
    <PageHeader eyebrow="Farmer assessment mode" title="Build a maize field assessment" body="A short guided flow with precise units, honest validation, and a complete review before the immutable result is saved." />
    {values.source === "demo" && <div className="mb-5"><Alert tone="warning" title="Synthetic demo preset active">You may edit these values. The assessment remains labelled synthetic unless you explicitly switch it to a manual record. <button type="button" className="font-bold underline" onClick={() => setValue("source", "manual")}>Use as manual record</button></Alert></div>}
    <ol className="mb-5 grid grid-cols-2 gap-2 lg:grid-cols-4" aria-label="Assessment progress">{steps.map(({ title, icon: Icon }, index) => <li key={title} className={`flex min-h-14 items-center gap-3 rounded-xl border px-3 text-sm font-bold ${index === step ? "border-deep bg-green-50 text-deep" : index < step ? "border-green-200 bg-white text-ink" : "border-line bg-white/65 text-muted"}`} aria-current={index === step ? "step" : undefined}><span className={`grid size-8 shrink-0 place-items-center rounded-lg ${index <= step ? "bg-deep text-white" : "bg-slate-100"}`}>{index < step ? <Check className="size-4" /> : <Icon className="size-4" />}</span>{title}</li>)}</ol>

    {Object.keys(errors).length > 0 && step === 3 && <div className="mb-4"><Alert tone="critical" title="Review the assessment fields">At least one value is outside a hard processing limit. Your other entries have been preserved.</Alert></div>}
    {submitError && <div className="mb-4"><Alert tone="critical" title="Assessment not saved">{submitError}</Alert></div>}

    <FormProvider {...methods}><form onSubmit={handleSubmit(onSubmit)} noValidate>
      <Card className="min-h-[31rem] p-5 sm:p-7">
        {step === 0 && <fieldset><legend className="text-2xl font-extrabold text-ink">Field context</legend><p className="mt-2 text-muted">Maize is fixed for this MVP. Use only a coarse location and non-sensitive field alias.</p><div className="mt-6 grid gap-5 md:grid-cols-2"><label><span className="label">Crop</span><input className="input bg-slate-50" value="Maize" disabled /><span className="help block">Other crops require separate models and reviewed advisory rules.</span></label><label><span className="label">Season <span className="font-normal text-muted">(optional)</span></span><input className="input" maxLength={30} placeholder="Example: 2025/26" {...methods.register("season")} /></label><label><span className="label">District <span className="font-normal text-muted">(optional, coarse)</span></span><input className="input" maxLength={80} placeholder="Example: Goromonzi" {...methods.register("district")} /><span className="help block">Do not enter exact GPS coordinates.</span></label><label><span className="label">Field reference <span className="font-normal text-muted">(optional alias)</span></span><input className="input" maxLength={80} placeholder="Example: North field" {...methods.register("farm_reference")} /><span className="help block">Avoid legal names, phone numbers, or national IDs.</span></label></div><div className="mt-7"><p className="label">Load a synthetic demonstration preset</p><div className="flex flex-wrap gap-2">{scenarios.data?.map((scenario) => <Button type="button" variant="secondary" key={scenario.id} onClick={() => reset({ ...scenario.values, language: locale, source: "demo" })}>{scenario.name}</Button>)}</div></div></fieldset>}
        {step === 1 && <fieldset><legend className="text-2xl font-extrabold text-ink">Climate observations</legend><p className="mt-2 text-muted">All weather values must describe the same assessment season.</p><div className="mt-6 grid gap-6 lg:grid-cols-3"><NumberField feature={features.rainfall_mm} helper="Total rainfall over the assessment season; do not enter a daily value." /><NumberField feature={features.temperature_c} helper="Mean temperature over the same season as the rainfall value." /><NumberField feature={features.humidity_pct} helper="Mean relative humidity over the same assessment season." /></div><div className="mt-6"><Alert tone="info" title="Hard limits versus model familiarity">Values inside these technical limits can be processed. The result may still show a prominent unfamiliar-input warning and lower confidence.</Alert></div></fieldset>}
        {step === 2 && <fieldset><legend className="text-2xl font-extrabold text-ink">Soil and recorded input</legend><p className="mt-2 text-muted">Record measured conditions and fertiliser already applied. MundaSense does not calculate or prescribe a dose.</p><div className="mt-6 grid gap-6 md:grid-cols-2"><NumberField feature={features.soil_ph} helper="Use a representative soil measurement where available." /><NumberField feature={features.fertilizer_kg_ha} helper="Record only the amount already applied in kg/ha." /></div><div className="mt-6"><Alert tone="warning" title="No input prescription">A simulated or predicted change must never be treated as a recommended fertiliser rate.</Alert></div></fieldset>}
        {step === 3 && <div><h2 className="text-2xl font-extrabold text-ink">Review before saving</h2><p className="mt-2 text-muted">Confirm units and the shared assessment period. Submission creates a versioned immutable snapshot.</p><div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[
          ["Seasonal rainfall", values.rainfall_mm, "mm / assessment season"], ["Mean temperature", values.temperature_c, "°C seasonal mean"], ["Mean humidity", values.humidity_pct, "% seasonal mean"], ["Soil pH", values.soil_ph, "pH"], ["Recorded fertiliser", values.fertilizer_kg_ha, "kg/ha already applied"], ["District", values.district || "Not recorded", "coarse location"],
        ].map(([label, value, unit]) => <div key={label as string} className="rounded-xl border border-line bg-pale/60 p-4"><p className="text-xs font-bold uppercase tracking-wider text-muted">{label}</p><p className="mt-1 text-lg font-extrabold text-ink">{String(value)} <span className="text-sm font-medium text-muted">{unit}</span></p></div>)}</div><div className="mt-6"><Alert tone="warning" title="Estimate, not a guarantee">The local model is trained on synthetic demonstration data. Review uncertainty, warnings, and referral guidance before relying on any result.</Alert></div></div>}
      </Card>
      <div className="mt-5 flex items-center justify-between gap-3"><Button type="button" variant="secondary" disabled={step === 0 || mutation.isPending} onClick={() => setStep((current) => Math.max(0, current - 1))}><ArrowLeft className="size-4" />Back</Button>{step < 3 ? <Button type="button" onClick={advance}>Continue<ArrowRight className="size-4" /></Button> : <Button type="submit" disabled={mutation.isPending || Object.keys(errors).length > 0}>{mutation.isPending ? <Spinner label="Running local assessment" /> : <><Leaf className="size-4" />Assess and save</>}</Button>}</div>
    </form></FormProvider>
  </div>;
}
