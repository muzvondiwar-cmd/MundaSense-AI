import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BarChart3, Database, Gauge } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { PageHeader, SectionHeader } from "../components/PageHeader";
import { Alert, Card, EmptyState, PageSkeleton } from "../components/ui";
import { api } from "../services/api";

const riskColors: Record<string, string> = {
  low: "#0D4F3C",
  moderate: "#E0A000",
  high: "#CF1737",
};

export default function InsightsPage() {
  const insights = useQuery({ queryKey: ["insights"], queryFn: api.insights });
  if (insights.isLoading) return <PageSkeleton />;
  if (!insights.data)
    return (
      <Alert tone="critical" title="Insights unavailable">
        The local analytics service could not be reached.
      </Alert>
    );
  const data = insights.data;
  if (!data.total_records)
    return (
      <EmptyState
        icon={<BarChart3 className="size-6" />}
        title="No records to analyse"
        body="Complete an assessment or seed demonstration data to populate insights."
      />
    );
  const inputLabels: Record<string, string> = {
    rainfall_mm: "Rainfall (mm)",
    fertilizer_kg_ha: "Fertiliser (kg/ha)",
    temperature_c: "Temperature (°C)",
    humidity_pct: "Humidity (%)",
    soil_ph: "Soil pH",
  };
  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Portfolio analytics"
        title="Insights across assessed fields"
        body="Explore local patterns without turning model estimates into field evidence. Every chart carries its unit and sample basis."
      />
      {data.contains_demo_data && (
        <Alert tone="warning" title="Demonstration records included">
          These charts include explicitly labelled synthetic demonstration
          assessments.
        </Alert>
      )}
      <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <Database className="size-6 text-teal" />
          <p className="mt-4 text-xs font-bold uppercase text-muted">Records</p>
          <p className="mt-1 text-3xl font-black text-ink">
            {data.total_records}
          </p>
        </Card>
        <Card className="p-5">
          <Gauge className="size-6 text-teal" />
          <p className="mt-4 text-xs font-bold uppercase text-muted">
            Data completeness
          </p>
          <p className="mt-1 text-3xl font-black text-ink">
            {data.data_completeness_pct.toFixed(0)}%
          </p>
        </Card>
        <Card className="p-5">
          <AlertTriangle className="size-6 text-gold" />
          <p className="mt-4 text-xs font-bold uppercase text-muted">
            Unusual inputs
          </p>
          <p className="mt-1 text-3xl font-black text-ink">
            {data.unusual_records}
          </p>
        </Card>
        <Card className="p-5">
          <BarChart3 className="size-6 text-teal" />
          <p className="mt-4 text-xs font-bold uppercase text-muted">
            Model versions
          </p>
          <p className="mt-1 text-3xl font-black text-ink">
            {data.model_versions.length}
          </p>
        </Card>
      </div>
      <SectionHeader
        title="Yield and risk patterns"
        body="Predicted yield is shown in tonnes per hectare; district risk uses an ordinal view where 0 is low, 1 moderate, and 2 high."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h2 className="font-extrabold text-ink">Predicted yield over time</h2>
          <p className="text-sm text-muted">Central estimate · t/ha</p>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <LineChart data={data.yield_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d9e3dc" />
                <XAxis dataKey="label" fontSize={11} />
                <YAxis unit=" t/ha" />
                <Tooltip
                  formatter={(value) => [
                    `${Number(value).toFixed(2)} t/ha`,
                    "Predicted yield",
                  ]}
                />
                <Line
                  dataKey="value"
                  name="Predicted yield"
                  stroke="#078B8B"
                  strokeWidth={3}
                  dot={{ fill: "#0D4F3C" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="p-4">
          <h2 className="font-extrabold text-ink">Risk distribution</h2>
          <p className="text-sm text-muted">
            Assessment count by provisional risk category
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={data.risk_distribution}
                  dataKey="value"
                  nameKey="label"
                  innerRadius={58}
                  outerRadius={94}
                  label
                >
                  {data.risk_distribution.map((item) => (
                    <Cell
                      key={item.label}
                      fill={riskColors[item.label] ?? "#078B8B"}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="p-4">
          <h2 className="font-extrabold text-ink">Risk by district</h2>
          <p className="text-sm text-muted">
            Mean ordinal risk · hover for sample size
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <BarChart data={data.risk_by_district}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d9e3dc" />
                <XAxis dataKey="label" fontSize={11} />
                <YAxis domain={[0, 2]} ticks={[0, 1, 2]} />
                <Tooltip
                  formatter={(value, _name, item) => [
                    `${Number(value).toFixed(2)} · n=${item.payload.sample_size}`,
                    "Mean risk",
                  ]}
                />
                <Bar dataKey="value" fill="#E0A000" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="p-4">
          <h2 className="font-extrabold text-ink">Most common model drivers</h2>
          <p className="text-sm text-muted">
            Top-three appearances across assessments
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <BarChart data={data.common_risk_drivers} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#d9e3dc" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis
                  dataKey="label"
                  type="category"
                  width={115}
                  fontSize={11}
                />
                <Tooltip />
                <Bar
                  dataKey="value"
                  name="Appearances"
                  fill="#078B8B"
                  radius={[0, 8, 8, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
      <SectionHeader
        title="Average recorded conditions"
        body="Averages describe the visible local record set; they are not agronomic targets."
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {Object.entries(data.average_inputs).map(([key, value]) => (
          <Card key={key} className="p-4">
            <p className="text-xs font-bold uppercase tracking-wide text-muted">
              {inputLabels[key] ?? key}
            </p>
            <p className="mt-2 text-2xl font-black text-ink">
              {value.toFixed(key === "soil_ph" ? 1 : 0)}
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}
