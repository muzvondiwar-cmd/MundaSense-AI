import type {
  AppConfig,
  AssessmentCreate,
  AssessmentResponse,
  DashboardResponse,
  DemoScenario,
  HealthResponse,
  HistoryResponse,
  Locale,
  ModelCardResponse,
  ScenarioSimulation,
} from "../types/api";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail: unknown,
  ) {
    super(message);
  }
}

const API_ROOT = import.meta.env.VITE_API_ROOT ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20_000);
  try {
    const response = await fetch(`${API_ROOT}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      signal: controller.signal,
    });
    if (!response.ok) {
      let detail: unknown = null;
      try {
        detail = await response.json();
      } catch {
        detail = await response.text();
      }
      throw new ApiError(`Request failed with status ${response.status}`, response.status, detail);
    }
    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  } finally {
    window.clearTimeout(timeout);
  }
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  config: (language: Locale) => request<AppConfig>(`/config?language=${language}`),
  demoScenarios: () => request<DemoScenario[]>("/demo-scenarios"),
  createAssessment: (payload: AssessmentCreate) =>
    request<AssessmentResponse>("/assessments", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getAssessment: (id: string, language: Locale) =>
    request<AssessmentResponse>(`/assessments/${encodeURIComponent(id)}?language=${language}`),
  listAssessments: (query = "") => request<HistoryResponse>(`/assessments${query}`),
  deleteAssessment: (id: string) =>
    request<void>(`/assessments/${encodeURIComponent(id)}`, { method: "DELETE" }),
  simulate: (baselineId: string, overrides: Record<string, number>, language: Locale) =>
    request<ScenarioSimulation>("/scenarios/simulate", {
      method: "POST",
      body: JSON.stringify({
        baseline_assessment_id: baselineId,
        overrides,
        language,
      }),
    }),
  dashboard: (query = "") => request<DashboardResponse>(`/dashboard/summary${query}`),
  modelCard: (language: Locale) => request<ModelCardResponse>(`/model-card?language=${language}`),
  exportUrl: (query = "") => `${API_ROOT}/assessments/export.csv${query}`,
  reportUrl: (id: string) => `${API_ROOT}/assessments/${encodeURIComponent(id)}/report`,
};

export function assessmentToCreate(result: AssessmentResponse): AssessmentCreate {
  return {
    crop: "maize",
    rainfall_mm: result.inputs.rainfall.value,
    fertilizer_kg_ha: result.inputs.fertilizer.value,
    temperature_c: result.inputs.temperature.value,
    humidity_pct: result.inputs.humidity.value,
    soil_ph: result.inputs.soil_ph.value,
    season: result.context.season,
    district: result.context.district,
    farm_reference: result.context.farm_reference,
    language: result.context.language,
    source: result.context.source,
  };
}
