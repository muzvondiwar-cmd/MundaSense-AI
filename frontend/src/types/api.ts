export type Locale = "en" | "sn";
export type Source = "manual" | "demo" | "scenario";
export type RiskBand = "low" | "moderate" | "high";
export type ConfidenceBand = "high" | "medium" | "low" | "insufficient";
export type DataStatus = "real" | "synthetic_demo";

export interface AssessmentCreate {
  crop: "maize";
  rainfall_mm: number;
  fertilizer_kg_ha: number;
  temperature_c: number;
  humidity_pct: number;
  soil_ph: number;
  season: string;
  district: string;
  farm_reference: string;
  language: Locale;
  source: Source;
}

export interface InputValue {
  value: number;
  unit: string;
}

export interface AssessmentResponse {
  assessment_id: string;
  created_at: string;
  inputs: {
    rainfall: InputValue;
    fertilizer: InputValue;
    temperature: InputValue;
    humidity: InputValue;
    soil_ph: InputValue;
  };
  context: {
    crop: "maize";
    season: string;
    district: string;
    farm_reference: string;
    language: Locale;
    source: Source;
  };
  prediction: {
    yield_t_ha: number;
    range_low_t_ha: number;
    range_high_t_ha: number;
    risk_band: RiskBand;
    risk_label: string;
    risk_explanation: string;
    confidence: {
      band: ConfidenceBand;
      score: number | null;
      method: string;
    };
  };
  drivers: Array<{
    feature: string;
    label: string;
    direction: "raises_yield" | "lowers_yield" | "neutral";
    importance: number;
    signed_contribution: number;
    value: number;
    unit: string;
    explanation: string;
    approximate: boolean;
  }>;
  warnings: Array<{
    code: string;
    severity: "info" | "warning" | "critical";
    title: string;
    message: string;
    feature: string | null;
  }>;
  advisory: {
    priority_action: string;
    message: string;
    reason: string;
    referral_required: boolean;
    referral_message: string | null;
    supporting_actions: Array<{ title: string; message: string; rule_id: string }>;
  };
  versions: { model: string; risk_policy: string; rules: string; app: string };
  data_status: DataStatus;
  synthetic_model: boolean;
  explanation_method: string;
  disclaimer: string;
  technical_metadata: Record<string, unknown>;
}

export interface HistoryItem {
  assessment_id: string;
  created_at: string;
  district: string;
  farm_reference: string;
  predicted_yield_t_ha: number;
  risk_band: RiskBand;
  confidence: ConfidenceBand;
  referral_required: boolean;
  data_status: DataStatus;
  source: Source;
  model_version: string;
  top_warning: string | null;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  districts: string[];
}

export interface FeatureConfig {
  key: keyof Pick<
    AssessmentCreate,
    "rainfall_mm" | "fertilizer_kg_ha" | "temperature_c" | "humidity_pct" | "soil_ph"
  >;
  label: string;
  unit: string;
  hard_min: number;
  hard_max: number;
  example: number;
}

export interface AppConfig {
  crop: "maize";
  features: FeatureConfig[];
  locales: Locale[];
  default_locale: Locale;
  model_version: string;
  app_version: string;
  extension_contact: string;
  demo_model: boolean;
}

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  values: AssessmentCreate;
}

export interface HealthResponse {
  ready: boolean;
  status: "local_system_ready" | "needs_attention";
  checks: Record<string, { ok: boolean; detail: string }>;
  app_version: string;
  model_version: string | null;
}

export interface ScenarioSimulation {
  baseline: AssessmentResponse;
  scenario: AssessmentResponse;
  delta: {
    yield_t_ha: number;
    range_low_t_ha: number;
    range_high_t_ha: number;
    risk_changed: boolean;
    confidence_changed: boolean;
  };
  persisted: false;
}

export interface DashboardResponse {
  kpis: {
    total_assessments: number;
    high_risk_assessments: number;
    average_predicted_yield_t_ha: number | null;
    low_confidence_assessments: number;
    referrals_required: number;
  };
  assessments_over_time: Array<{ label: string; count: number }>;
  risk_distribution: Array<{ label: string; count: number }>;
  confidence_distribution: Array<{ label: string; count: number }>;
  frequent_drivers: Array<{ label: string; count: number }>;
  yield_by_district: Array<{ label: string; average_yield_t_ha: number; sample_size: number }>;
  priority_cases: HistoryItem[];
  contains_synthetic_demo: boolean;
  small_sample: boolean;
  active_filters: Record<string, string | boolean | null>;
}

export interface ModelCardResponse {
  model_version: string;
  status: string;
  champion: string;
  created_at: string;
  explanation_method: string;
  interval_method: string;
  metrics: Array<{ label: string; value: number; unit: string | null }>;
  features: FeatureConfig[];
  limitations: string[];
  training_ranges: Record<string, Record<string, number>>;
}
