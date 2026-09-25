import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Archive,
  ArrowLeft,
  ArrowRight,
  Download,
  FileSearch,
  FilterX,
  Search,
  Sprout,
} from "lucide-react";
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { ConfidenceBadge, RiskBadge } from "../components/RiskBadge";
import {
  Alert,
  Badge,
  Button,
  Card,
  EmptyState,
  Modal,
  PageSkeleton,
} from "../components/ui";
import { api } from "../services/api";

export default function HistoryPage() {
  const [params, setParams] = useSearchParams();
  const queryString = params.toString() ? `?${params.toString()}` : "";
  const history = useQuery({
    queryKey: ["history", queryString],
    queryFn: () => api.listAssessments(queryString),
  });
  const queryClient = useQueryClient();
  const [archiveId, setArchiveId] = useState<string | null>(null);
  const page = Math.max(1, Number(params.get("page") ?? 1));
  const pageSize = 10;
  const archive = useMutation({
    mutationFn: api.archiveAssessment,
    onSuccess: async () => {
      setArchiveId(null);
      await queryClient.invalidateQueries({ queryKey: ["history"] });
    },
  });
  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    value ? next.set(key, value) : next.delete(key);
    setParams(next, { replace: true });
  };
  if (history.isLoading) return <PageSkeleton />;
  if (!history.data)
    return (
      <Alert tone="critical" title="History unavailable">
        The local assessment database could not be reached. Retry when the
        backend is ready.
      </Alert>
    );
  const pageCount = Math.max(1, Math.ceil(history.data.total / pageSize));
  const visibleItems = history.data.items.slice(
    (Math.min(page, pageCount) - 1) * pageSize,
    Math.min(page, pageCount) * pageSize,
  );
  const setPage = (nextPage: number) => {
    const next = new URLSearchParams(params);
    next.set("page", String(nextPage));
    setParams(next, { replace: true });
  };

  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Immutable local records"
        title="Assessment history"
        body="Search and filter saved snapshots without re-running the current model. Corrections require a new assessment."
        actions={
          <>
            <a
              href={api.exportUrl(queryString)}
              className="button button-secondary"
            >
              <Download className="size-4" />
              Export current view
            </a>
            <Link to="/assess/new" className="button button-primary">
              <Sprout className="size-4" />
              New assessment
            </Link>
          </>
        }
      />
      <Card className="p-4">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-7">
          <label className="xl:col-span-2">
            <span className="label">Search ID, district, or field alias</span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-3 size-5 text-muted" />
              <input
                className="input pl-10"
                value={params.get("search") ?? ""}
                onChange={(e) => setFilter("search", e.target.value)}
                placeholder="Search local records"
              />
            </div>
          </label>
          <label>
            <span className="label">Risk</span>
            <select
              className="input"
              value={params.get("risk") ?? ""}
              onChange={(e) => setFilter("risk", e.target.value)}
            >
              <option value="">All</option>
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
              <option value="">All</option>
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
              <option value="">All</option>
              <option value="real">Real</option>
              <option value="synthetic_demo">Synthetic demo</option>
            </select>
          </label>
          <label>
            <span className="label">Sort</span>
            <select
              className="input"
              value={params.get("sort") ?? "newest"}
              onChange={(e) => setFilter("sort", e.target.value)}
            >
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="highest_risk">Highest risk</option>
              <option value="lowest_confidence">Lowest confidence</option>
            </select>
          </label>
        </div>
        {params.size > 0 && (
          <Button
            className="mt-3"
            variant="ghost"
            onClick={() => setParams({})}
          >
            <FilterX className="size-4" />
            Clear filters
          </Button>
        )}
      </Card>
      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm font-semibold text-muted">
          {history.data.total} saved{" "}
          {history.data.total === 1 ? "assessment" : "assessments"}
        </p>
        {history.data.items.some(
          (item) => item.data_status === "synthetic_demo",
        ) && <Badge tone="gold">Synthetic demo records visible</Badge>}
      </div>
      {history.data.total === 0 ? (
        <div className="mt-5">
          <EmptyState
            icon={<FileSearch className="size-6" />}
            title="No saved records found"
            body={
              params.size
                ? "No local records match these filters. Clear them to widen the view."
                : "Complete a maize assessment to create the first immutable local snapshot."
            }
            action={
              params.size ? (
                <Button onClick={() => setParams({})}>Clear filters</Button>
              ) : (
                <Link className="button button-primary" to="/assess/new">
                  Start assessment
                </Link>
              )
            }
          />
        </div>
      ) : (
        <>
          <div className="mt-4 hidden overflow-hidden rounded-2xl border border-line bg-white lg:block">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-pale text-xs uppercase tracking-wider text-muted">
                <tr>
                  <th className="p-3">Created</th>
                  <th className="p-3">Field</th>
                  <th className="p-3">Yield</th>
                  <th className="p-3">Risk</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {visibleItems.map((item) => (
                  <tr
                    key={item.assessment_id}
                    className="border-t border-line hover:bg-green-50/50"
                  >
                    <td className="p-3">
                      <p className="font-semibold text-ink">
                        {new Date(item.created_at).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-muted">
                        {new Date(item.created_at).toLocaleTimeString()}
                      </p>
                    </td>
                    <td className="max-w-56 p-3">
                      <p className="truncate font-semibold text-ink">
                        {item.farm_reference || "Unnamed field"}
                      </p>
                      <p className="truncate text-xs text-muted">
                        {item.district || "No district"} ·{" "}
                        {item.assessment_id.slice(0, 8)}
                      </p>
                    </td>
                    <td className="p-3 font-extrabold text-ink">
                      {item.predicted_yield_t_ha.toFixed(2)} t/ha
                    </td>
                    <td className="p-3">
                      <RiskBadge risk={item.risk_band} />
                    </td>
                    <td className="p-3">
                      <ConfidenceBadge confidence={item.confidence} />
                    </td>
                    <td className="p-3">
                      <div className="flex flex-wrap gap-1">
                        {item.referral_required && (
                          <Badge tone="red">Referral</Badge>
                        )}
                        <Badge
                          tone={
                            item.data_status === "synthetic_demo"
                              ? "gold"
                              : "green"
                          }
                        >
                          {item.data_status === "synthetic_demo"
                            ? "Demo"
                            : "Real"}
                        </Badge>
                        <Badge
                          tone={
                            item.sync_status === "synchronized"
                              ? "teal"
                              : item.sync_status === "failed"
                                ? "red"
                                : "gold"
                          }
                        >
                          {item.sync_status}
                        </Badge>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex">
                        <button
                          className="icon-button"
                          aria-label={`Archive assessment ${item.assessment_id}`}
                          onClick={() => setArchiveId(item.assessment_id)}
                        >
                          <Archive className="size-4" />
                        </button>
                        <Link
                          className="icon-button"
                          aria-label={`Open assessment ${item.assessment_id}`}
                          to={`/history/${item.assessment_id}`}
                        >
                          <ArrowRight className="size-5" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 grid gap-3 lg:hidden">
            {visibleItems.map((item) => (
              <Card key={item.assessment_id} className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <Link
                    to={`/history/${item.assessment_id}`}
                    className="min-w-0 flex-1"
                  >
                    <p className="font-extrabold text-ink">
                      {item.farm_reference || "Unnamed field"}
                    </p>
                    <p className="mt-1 text-xs text-muted">
                      {item.district || "No district"} ·{" "}
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </Link>
                  <button
                    className="icon-button"
                    aria-label={`Archive assessment ${item.assessment_id}`}
                    onClick={() => setArchiveId(item.assessment_id)}
                  >
                    <Archive className="size-4" />
                  </button>
                </div>
                <p className="mt-4 text-2xl font-black text-ink">
                  {item.predicted_yield_t_ha.toFixed(2)}{" "}
                  <span className="text-sm text-muted">t/ha</span>
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <RiskBadge risk={item.risk_band} />
                  <ConfidenceBadge confidence={item.confidence} />
                  {item.data_status === "synthetic_demo" && (
                    <Badge tone="gold">Synthetic demo</Badge>
                  )}
                  <Badge
                    tone={item.sync_status === "synchronized" ? "teal" : "gold"}
                  >
                    {item.sync_status}
                  </Badge>
                </div>
              </Card>
            ))}
          </div>
          {pageCount > 1 && (
            <div className="mt-5 flex items-center justify-center gap-3">
              <Button
                variant="secondary"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                <ArrowLeft className="size-4" />
                Previous
              </Button>
              <span className="text-sm font-bold text-muted">
                Page {Math.min(page, pageCount)} of {pageCount}
              </span>
              <Button
                variant="secondary"
                disabled={page >= pageCount}
                onClick={() => setPage(page + 1)}
              >
                Next
                <ArrowRight className="size-4" />
              </Button>
            </div>
          )}
        </>
      )}
      <Modal
        open={Boolean(archiveId)}
        title="Archive this assessment?"
        onClose={() => setArchiveId(null)}
      >
        <p className="leading-7 text-muted">
          The assessment will leave the active history and dashboard but remain
          in SQLite for audit and recovery.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setArchiveId(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            disabled={archive.isPending}
            onClick={() => archiveId && archive.mutate(archiveId)}
          >
            Archive assessment
          </Button>
        </div>
      </Modal>
    </div>
  );
}
