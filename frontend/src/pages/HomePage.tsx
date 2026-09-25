import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  BarChart3,
  Beaker,
  CheckCircle2,
  CloudOff,
  Leaf,
  Play,
  ShieldCheck,
  Sparkles,
  Sprout,
  TriangleAlert,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { PageHeader, SectionHeader } from "../components/PageHeader";
import { Alert, Badge, Button, Card, PageSkeleton } from "../components/ui";
import { usePreferences } from "../app/Preferences";
import { api } from "../services/api";

export default function HomePage() {
  const navigate = useNavigate();
  const { locale } = usePreferences();
  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const scenarios = useQuery({
    queryKey: ["demo-scenarios"],
    queryFn: api.demoScenarios,
  });
  const config = useQuery({
    queryKey: ["config", locale],
    queryFn: () => api.config(locale),
  });
  if (scenarios.isLoading || config.isLoading) return <PageSkeleton />;

  return (
    <div className="page-enter space-y-6">
      <section className="adaptive-gradient-card field-texture overflow-hidden rounded-[1.6rem] border border-green-200 bg-gradient-to-br from-white via-green-50 to-teal-50 p-6 shadow-[0_24px_70px_rgba(22,58,36,.10)] sm:p-9 lg:p-12">
        <div className="max-w-4xl">
          <Badge tone="teal">
            <Sparkles className="size-3.5" />
            Offline-first maize decision support
          </Badge>
          <h1 className="mt-5 text-5xl font-black leading-[1.02] tracking-[-.045em] text-ink sm:text-6xl lg:text-7xl">
            Know the risk.
            <br />
            <span className="text-gold">Understand the cause.</span>
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-600">
            Turn five seasonal field observations into an explainable
            maize-yield range, a provisional risk band, and one guarded next
            action—without sending farm data to a cloud service.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link to="/assess/new" className="button button-primary">
              <Sprout className="size-5" />
              Start maize assessment
            </Link>
            <Link to="/dashboard" className="button button-secondary">
              <BarChart3 className="size-5" />
              Open dashboard
            </Link>
            <Link
              to="/assess/new?scenario=balanced"
              className="button button-ghost"
            >
              <Play className="size-5" />
              Explore demonstration data
            </Link>
          </div>
          <div className="mt-7 flex flex-wrap gap-2 text-sm">
            <Badge tone={health.data?.ready ? "green" : "red"}>
              {health.data?.ready ? (
                <ShieldCheck className="size-3.5" />
              ) : (
                <CloudOff className="size-3.5" />
              )}
              {health.data?.ready
                ? "Local inference ready"
                : "Backend unavailable"}
            </Badge>
            <Badge tone="neutral">
              Model {config.data?.model_version ?? "checking"}
            </Badge>
            <Badge tone="gold">Synthetic model · not field-validated</Badge>
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          [
            BarChart3,
            "Estimate risk honestly",
            "See a central yield estimate, plausible range, provisional risk band, and confidence together.",
          ],
          [
            Beaker,
            "Understand model drivers",
            "Explore the three strongest model associations without presenting them as biological causes.",
          ],
          [
            CheckCircle2,
            "Take a safer next step",
            "Receive one bounded action from versioned rules and a clear referral signal when evidence is weak.",
          ],
        ].map(([Icon, title, body]) => (
          <Card
            key={title as string}
            className="p-5 transition hover:-translate-y-1 hover:shadow-xl motion-reduce:transform-none"
          >
            <div className="grid size-11 place-items-center rounded-xl bg-green-50 text-deep">
              <Icon className="size-6" />
            </div>
            <h2 className="mt-4 text-xl font-extrabold text-ink">
              {title as string}
            </h2>
            <p className="mt-2 leading-7 text-muted">{body as string}</p>
          </Card>
        ))}
      </div>

      <SectionHeader
        title="Try a transparent demo journey"
        body="Presets come from the local backend and remain visibly labelled as synthetic even if you edit them."
      />
      {scenarios.isError ? (
        <Alert tone="critical" title="Demo scenarios unavailable">
          Start the local API and try again.
        </Alert>
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          {scenarios.data?.map((scenario, index) => (
            <Card key={scenario.id} className="flex flex-col p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="grid size-10 place-items-center rounded-xl bg-pale font-black text-deep">
                  {index + 1}
                </div>
                <Badge tone="gold">Synthetic demo</Badge>
              </div>
              <h3 className="mt-4 text-xl font-extrabold text-ink">
                {scenario.name}
              </h3>
              <p className="mt-2 flex-1 leading-7 text-muted">
                {scenario.description}
              </p>
              <Button
                variant="secondary"
                className="mt-5 w-full"
                onClick={() => navigate(`/assess/new?scenario=${scenario.id}`)}
              >
                Load this scenario
                <ArrowRight className="size-4" />
              </Button>
            </Card>
          ))}
        </div>
      )}

      <SectionHeader title="How it works" />
      <div className="grid gap-3 md:grid-cols-3">
        {[
          [
            "01",
            "Record conditions",
            "Enter one season's rainfall, temperature, humidity, soil pH, and fertiliser already applied.",
          ],
          [
            "02",
            "Read uncertainty",
            "Review the range, risk, confidence, drivers, and unusual-input warnings together.",
          ],
          [
            "03",
            "Use field judgement",
            "Take the guarded next step and involve an extension officer when referral is triggered.",
          ],
        ].map(([number, title, body]) => (
          <div key={number} className="border-l border-green-300 py-2 pl-5">
            <p className="text-sm font-black text-teal">{number}</p>
            <h3 className="mt-1 text-lg font-extrabold text-ink">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
          </div>
        ))}
      </div>

      <Alert tone="warning" title="Responsible use">
        MundaSense is maize-only decision support. It does not prescribe input
        doses, guarantee harvests, replace field inspection, or provide
        field-validated truth.{" "}
        <Link to="/model" className="font-bold underline">
          Read the model card
        </Link>
        .
      </Alert>
    </div>
  );
}
