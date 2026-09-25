import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CalendarCheck,
  CalendarRange,
  ClipboardList,
  Cloud,
  Cpu,
  FilterX,
  MapPin,
  ShieldAlert,
  Sprout,
  Users,
} from "lucide-react";
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
import { Link, useSearchParams } from "react-router-dom";

import { PageHeader, SectionHeader } from "../components/PageHeader";
import { ConfidenceBadge, RiskBadge } from "../components/RiskBadge";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  PageSkeleton,
} from "../components/ui";
import { api } from "../services/api";
import { useOfflineSync } from "../app/OfflineSync";

const riskColors: Record<string, string> = {
  low: "#2e7d32",
  moderate: "#d99a00",
  high: "#a62b24",
};
const confidenceColors = ["#00796b", "#d99a00", "#d86f25", "#a62b24"];

export default function DashboardPage() {
  const [params, setParams] = useSearchParams();
  const queryString = params.toString() ? `?${params.toString()}` : "";
  const dashboard = useQuery({
    queryKey: ["dashboard", queryString],
    queryFn: () => api.dashboard(queryString),
  });
  const farms = useQuery({
    queryKey: ["farms", "dashboard"],
    queryFn: api.farms,
  });
  const fields = useQuery({
    queryKey: ["fields", "dashboard"],
    queryFn: () => api.fields(),
  });
  const { pendingCount, failedCount } = useOfflineSync();
  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    value ? next.set(key, value) : next.delete(key);
    setParams(next, { replace: true });
  };
  if (dashboard.isLoading) return <PageSkeleton />;
  if (!dashboard.data)
    return (
      <Alert tone="critical" title="Dashboard unavailable">
        The local records service could not be reached. Retry when the backend
        is ready.
      </Alert>
    );
  const data = dashboard.data;
  const kpiCards = [
    {
      Icon: ClipboardList,
      label: "Total assessments",
      value: data.kpis.total_assessments,
      help: "Saved snapshots in this filtered view",
    },
    {
      Icon: AlertTriangle,
      label: "High risk",
      value: data.kpis.high_risk_assessments,
      help: "Below the provisional high-risk threshold",
    },
    {
      Icon: BarChart3,
      label: "Average yield",
      value:
        data.kpis.average_predicted_yield_t_ha == null
          ? "—"
          : `${data.kpis.average_predicted_yield_t_ha.toFixed(2)} t/ha`,
      help: "Mean central estimate; not observed yield",
    },
    {
      Icon: ShieldAlert,
      label: "Low confidence",
      value: data.kpis.low_confidence_assessments,
      help: "Low or insufficient model basis",
    },
    {
      Icon: Users,
      label: "Referrals",
      value: data.kpis.referrals_required,
      help: "Cases requiring extension review",
    },
    {
      Icon: CalendarCheck,
      label: "This season",
      value: data.kpis.assessments_this_season,
      help: "Assessments labelled 2025/26",
    },
    {
      Icon: Cloud,
      label: "Awaiting sync",
      value: pendingCount + failedCount + data.kpis.awaiting_synchronization,
      help: "Browser and backend pending records",
    },
    {
      Icon: Cpu,
      label: "Model version",
      value: data.model_version || "—",
      help: "Model used for new predictions",
    },
  ];

  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Extension Officer mode"
        title="Where does attention belong?"
        body="Every summary and priority case below is calculated from persisted local assessment snapshots—never from a hard-coded dashboard array."
        actions={
          <Link to="/assess/new" className="button button-primary">
            <Sprout className="size-4" />
            New assessment
          </Link>
        }
      />
      {data.contains_synthetic_demo && (
        <Alert tone="warning" title="Synthetic demo data included">
          At least one visible record is derived from a demo or scenario. Use
          the data-status filter before interpreting aggregates.
        </Alert>
      )}
      {data.small_sample && (
        <div className="mt-3">
          <Alert tone="info" title="Small local sample">
            Fewer than ten records match this view. Aggregates may be unstable
            and should not be generalized.
          </Alert>
        </div>
      )}
      <Card className="mt-5 p-4">
        <p className="mb-3 text-xs font-bold uppercase tracking-wider text-muted">
          Farm context filters
        </p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <label>
            <span className="label">Province</span>
            <select
              className="input"
              value={params.get("province") ?? ""}
              onChange={(event) => setFilter("province", event.target.value)}
            >
              <option value="">All provinces</option>
              {Array.from(
                new Set((farms.data ?? []).map((item) => item.province)),
              )
                .sort()
                .map((item) => (
                  <option key={item}>{item}</option>
                ))}
            </select>
          </label>
          <label>
            <span className="label">District</span>
            <select
              className="input"
              value={params.get("district") ?? ""}
              onChange={(event) => setFilter("district", event.target.value)}
            >
              <option value="">All districts</option>
              {Array.from(
                new Set((farms.data ?? []).map((item) => item.district)),
              )
                .sort()
                .map((item) => (
                  <option key={item}>{item}</option>
                ))}
            </select>
          </label>
          <label>
            <span className="label">Farm or field</span>
            <select
              className="input"
              value={params.get("field") ?? ""}
              onChange={(event) => setFilter("field", event.target.value)}
            >
              <option value="">All fields</option>
              {fields.data?.map((field) => (
                <option key={field.id} value={field.name}>
                  {farms.data?.find((farm) => farm.id === field.farm_id)
                    ?.name ?? "Farm"}{" "}
                  · {field.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span className="label">Season</span>
            <select
              className="input"
              value={params.get("season") ?? ""}
              onChange={(event) => setFilter("season", event.target.value)}
            >
              <option value="">All seasons</option>
              <option>2025/26</option>
              <option>2024/25</option>
              <option>2023/24</option>
            </select>
          </label>
        </div>
      </Card>

      <Card className="mt-5 p-4">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          <label>
            <span className="label">From date</span>
            <input
              type="date"
              className="input"
              value={params.get("from_date") ?? ""}
              onChange={(e) => setFilter("from_date", e.target.value)}
            />
          </label>
          <label>
            <span className="label">To date</span>
            <input
              type="date"
              className="input"
              value={params.get("to_date") ?? ""}
              onChange={(e) => setFilter("to_date", e.target.value)}
            />
          </label>
          <label>
            <span className="label">Risk</span>
            <select
              className="input"
              value={params.get("risk") ?? ""}
              onChange={(e) => setFilter("risk", e.target.value)}
            >
              <option value="">All risk bands</option>
              <option value="high">High</option>
              <option value="moderate">Moderate</option>
              <option value="low">Low</option>
            </select>
          </label>
          <label>
            <span className="label">Confidence</span>
            <select
              className="input"
              value={params.get("confidence") ?? ""}
              onChange={(e) => setFilter("confidence", e.target.value)}
            >
              <option value="">All confidence</option>
              <option value="insufficient">Insufficient</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>
            <span className="label">Referral</span>
            <select
              className="input"
              value={params.get("referral") ?? ""}
              onChange={(e) => setFilter("referral", e.target.value)}
            >
              <option value="">All</option>
              <option value="true">Required</option>
              <option value="false">Not required</option>
            </select>
          </label>
          <label>
            <span className="label">Data status</span>
            <select
              className="input"
              value={params.get("data_status") ?? ""}
              onChange={(e) => setFilter("data_status", e.target.value)}
            >
              <option value="">All records</option>
              <option value="real">Real assessments</option>
              <option value="synthetic_demo">Synthetic demo</option>
            </select>
          </label>
        </div>
        {params.size > 0 && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold uppercase text-muted">
              Active filters
            </span>
            {Array.from(params.entries()).map(([key, value]) => (
              <button
                key={key}
                className="badge badge-teal"
                onClick={() => setFilter(key, "")}
              >
                {key.replace("_", " ")}: {value} ×
              </button>
            ))}
            <Button variant="ghost" onClick={() => setParams({})}>
              <FilterX className="size-4" />
              Clear all
            </Button>
          </div>
        )}
      </Card>

      <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map(({ Icon, label, value, help }) => (
          <Card key={label} className="p-4">
            <div className="flex items-start justify-between">
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase tracking-wider text-muted">
                  {label}
                </p>
                <p className="mt-2 truncate text-3xl font-black text-ink">
                  {String(value)}
                </p>
              </div>
              <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-pale text-deep">
                <Icon className="size-5" />
              </div>
            </div>
            <p className="mt-3 text-xs leading-5 text-muted">{help}</p>
          </Card>
        ))}
      </div>

      {data.kpis.total_assessments === 0 ? (
        <div className="mt-6">
          <EmptyState
            icon={<CalendarRange className="size-6" />}
            title="No records match this view"
            body="Clear filters or run a maize assessment to populate the local dashboard."
            action={
              <Button onClick={() => setParams({})}>Clear filters</Button>
            }
          />
        </div>
      ) : (
        <>
          <SectionHeader
            title="Assessment patterns"
            body="Charts remain paired with labels and the priority case list below. Select a risk bar to cross-filter."
          />
          <div className="grid gap-4 lg:grid-cols-2">
            <Card className="p-4">
              <h3 className="font-extrabold text-ink">Predicted yield trend</h3>
              <p className="text-sm text-muted">
                Daily average model estimate; sample size appears in the
                tooltip.
              </p>
              <div
                className="mt-4 h-64"
                role="img"
                aria-label={data.yield_over_time
                  .map(
                    (item) =>
                      `${item.label}: ${item.average_yield_t_ha.toFixed(2)} tonnes per hectare`,
                  )
                  .join(", ")}
              >
                <ResponsiveContainer>
                  <LineChart data={data.yield_over_time}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#dce9dd" />
                    <XAxis dataKey="label" fontSize={11} />
                    <YAxis unit=" t/ha" />
                    <Tooltip
                      formatter={(value, _name, item) => [
                        `${Number(value).toFixed(2)} t/ha · n=${item.payload.sample_size}`,
                        "Average estimate",
                      ]}
                    />
                    <Line
                      type="monotone"
                      dataKey="average_yield_t_ha"
                      name="Average predicted yield"
                      stroke="#078B8B"
                      strokeWidth={3}
                      dot={{ fill: "#0D4F3C" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
            <Card className="p-4">
              <h3 className="font-extrabold text-ink">Risk distribution</h3>
              <p className="text-sm text-muted">
                Click a segment to filter the full dashboard.
              </p>
              <div
                className="mt-4 h-64"
                role="img"
                aria-label={data.risk_distribution
                  .map((item) => `${item.label}: ${item.count}`)
                  .join(", ")}
              >
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={data.risk_distribution}
                      dataKey="count"
                      nameKey="label"
                      innerRadius={52}
                      outerRadius={84}
                      paddingAngle={3}
                      label
                    >
                      {data.risk_distribution.map((item) => (
                        <Cell
                          key={item.label}
                          fill={riskColors[item.label]}
                          className="cursor-pointer"
                          onClick={() => setFilter("risk", item.label)}
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
              <h3 className="font-extrabold text-ink">
                Confidence distribution
              </h3>
              <p className="text-sm text-muted">
                Deterministic reliability labels, not outcome probabilities.
              </p>
              <div
                className="mt-4 h-64"
                role="img"
                aria-label={data.confidence_distribution
                  .map((item) => `${item.label}: ${item.count}`)
                  .join(", ")}
              >
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={data.confidence_distribution}
                      dataKey="count"
                      nameKey="label"
                      innerRadius={50}
                      outerRadius={82}
                      paddingAngle={3}
                      label
                    >
                      {data.confidence_distribution.map((item, index) => (
                        <Cell key={item.label} fill={confidenceColors[index]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>
            <Card className="p-4">
              <h3 className="font-extrabold text-ink">
                Frequent model drivers
              </h3>
              <p className="text-sm text-muted">
                Count of top-three appearances across visible records.
              </p>
              <div
                className="mt-4 h-64"
                role="img"
                aria-label={data.frequent_drivers
                  .map((item) => `${item.label}: ${item.count}`)
                  .join(", ")}
              >
                <ResponsiveContainer>
                  <BarChart data={data.frequent_drivers} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#dce9dd" />
                    <XAxis type="number" allowDecimals={false} />
                    <YAxis
                      type="category"
                      dataKey="label"
                      width={110}
                      fontSize={11}
                    />
                    <Tooltip />
                    <Bar dataKey="count" fill="#00796b" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          {data.yield_by_district.length > 0 && (
            <Card className="mt-4 p-4">
              <div className="flex items-center gap-2">
                <MapPin className="size-5 text-teal" />
                <h3 className="font-extrabold text-ink">
                  Average predicted yield by coarse district
                </h3>
              </div>
              <p className="mt-1 text-sm text-muted">
                Sample size is shown in the tooltip; these are model estimates,
                not observed harvest outcomes.
              </p>
              <div
                className="mt-4 h-72"
                role="img"
                aria-label={data.yield_by_district
                  .map(
                    (item) =>
                      `${item.label}: ${item.average_yield_t_ha.toFixed(2)} tonnes per hectare from ${item.sample_size} assessments`,
                  )
                  .join(", ")}
              >
                <ResponsiveContainer>
                  <BarChart data={data.yield_by_district}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#dce9dd" />
                    <XAxis dataKey="label" fontSize={11} />
                    <YAxis unit=" t/ha" />
                    <Tooltip
                      formatter={(value, _name, item) => [
                        `${Number(value).toFixed(2)} t/ha · n=${item.payload.sample_size}`,
                        "Average estimate",
                      ]}
                    />
                    <Bar
                      dataKey="average_yield_t_ha"
                      fill="#2e7d32"
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {data.data_quality_alerts.length > 0 && (
            <Card className="mt-4 p-4">
              <div className="flex items-center gap-2">
                <ShieldAlert className="size-5 text-gold" />
                <h3 className="font-extrabold text-ink">Data-quality alerts</h3>
              </div>
              <p className="mt-1 text-sm text-muted">
                Review these records before using them for field decisions.
              </p>
              <div className="mt-4 grid gap-2">
                {data.data_quality_alerts.map((item) => (
                  <Link
                    key={item.assessment_id}
                    to={`/history/${item.assessment_id}`}
                    className="rounded-xl border border-line bg-surface-muted p-3 text-sm transition hover:border-gold"
                  >
                    <span className="font-bold text-ink">
                      {item.farm_reference || item.assessment_id}
                    </span>{" "}
                    <span className="text-muted">— {item.top_warning}</span>
                  </Link>
                ))}
              </div>
            </Card>
          )}

          <SectionHeader
            title="Priority cases"
            body="Transparent order: referral first, then high risk, low confidence, and recency. No hidden AI score."
          />
          <div className="grid gap-3">
            {data.priority_cases.map((item) => (
              <Link
                key={item.assessment_id}
                to={`/history/${item.assessment_id}`}
                className="card flex flex-col gap-3 p-4 transition hover:border-green-300 hover:shadow-lg sm:flex-row sm:items-center"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-mono text-xs text-muted">
                    {item.assessment_id}
                  </p>
                  <p className="mt-1 font-extrabold text-ink">
                    {item.farm_reference || "Unnamed field"}
                  </p>
                  <p className="mt-1 text-sm text-muted">
                    {item.district || "No district"} ·{" "}
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <RiskBadge risk={item.risk_band} />
                  <ConfidenceBadge confidence={item.confidence} />
                  {item.referral_required && <Badge tone="red">Referral</Badge>}
                  <span className="font-bold text-ink">
                    {item.predicted_yield_t_ha.toFixed(2)} t/ha
                  </span>
                  <ArrowRight className="size-5 text-teal" />
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
