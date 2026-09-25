from __future__ import annotations

import os
from collections import Counter, defaultdict
from datetime import date
from html import escape
from statistics import fmean
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from backend.dependencies import Runtime, get_runtime
from backend.schemas import (
    AppConfigResponse,
    AssessmentCreate,
    AssessmentResponse,
    CountPoint,
    DashboardKpis,
    DashboardResponse,
    DemoScenario,
    FeatureConfig,
    HealthCheck,
    HealthResponse,
    HistoryResponse,
    ModelCardResponse,
    ModelMetric,
    ScenarioDelta,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
    YieldPoint,
)
from backend.serializers import derive_data_status, history_item, serialize_result
from mundasense.config import project_root
from mundasense.constants import APP_VERSION, FEATURE_SPEC
from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.schemas import AssessmentResult, AssessmentValidationError

ALLOWED_FEATURES = frozenset(FEATURE_SPEC)
DEFAULT_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
)


def _cors_origins() -> list[str]:
    configured = os.getenv("MUNDASENSE_CORS_ORIGINS", "")
    return [item.strip() for item in configured.split(",") if item.strip()] or list(DEFAULT_ORIGINS)


def _field_configs(runtime: Runtime, locale: str = "en") -> list[FeatureConfig]:
    return [
        FeatureConfig(
            key=key,
            label=runtime.translator.t(spec["display_key"], locale),
            unit=spec["unit"],
            hard_min=spec["hard_min"],
            hard_max=spec["hard_max"],
            example=spec["example"],
        )
        for key, spec in FEATURE_SPEC.items()
    ]


def _all_results(runtime: Runtime) -> list[AssessmentResult]:
    rows = runtime.repository.list(limit=2_000)
    return [result for row in rows if (result := runtime.repository.get(row["id"]))]


def _filtered_results(
    runtime: Runtime,
    *,
    search: str | None = None,
    risk: str | None = None,
    confidence: str | None = None,
    district: str | None = None,
    referral: bool | None = None,
    data_status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    sort: str = "newest",
) -> list[AssessmentResult]:
    rows = runtime.repository.list(
        risk=risk,
        confidence=confidence,
        district=district,
        from_date=from_date,
        to_date=to_date,
        limit=2_000,
    )
    results = [result for row in rows if (result := runtime.repository.get(row["id"]))]
    if search:
        needle = search.casefold()
        results = [
            result
            for result in results
            if needle in result.assessment_id.casefold()
            or needle in result.validated_inputs.district.casefold()
            or needle in result.validated_inputs.farm_reference.casefold()
        ]
    if referral is not None:
        results = [result for result in results if result.referral_required is referral]
    if data_status:
        results = [result for result in results if derive_data_status(result) == data_status]
    risk_rank = {"low": 0, "moderate": 1, "high": 2}
    confidence_rank = {"high": 0, "medium": 1, "low": 2, "insufficient": 3}
    if sort == "oldest":
        results.sort(key=lambda item: item.created_at)
    elif sort == "highest_risk":
        results.sort(key=lambda item: (risk_rank[item.risk_code], item.created_at), reverse=True)
    elif sort == "lowest_confidence":
        results.sort(
            key=lambda item: (confidence_rank[item.confidence_code], item.created_at),
            reverse=True,
        )
    else:
        results.sort(key=lambda item: item.created_at, reverse=True)
    return results


def _validation_detail(exc: AssessmentValidationError) -> dict[str, object]:
    items = []
    for message in exc.errors:
        field = message.split(" ", 1)[0] if " " in message else "assessment"
        items.append({"field": field, "message": message})
    return {"code": "assessment_validation_error", "errors": items}


def _report_html(result: AssessmentResponse) -> str:
    def safe(value: object) -> str:
        return escape(str(value), quote=True)

    driver_rows = "".join(
        f"<li><strong>{safe(driver.label)}</strong> — {safe(driver.explanation)} "
        f"({safe(driver.value)} {safe(driver.unit)})</li>"
        for driver in result.drivers
    )
    warning_rows = (
        "".join(
            f"<li><strong>{safe(item.title)}</strong> — {safe(item.message)}</li>"
            for item in result.warnings
        )
        or "<li>No unusual-input warnings were recorded.</li>"
    )
    values = [
        ("Seasonal rainfall", result.inputs.rainfall),
        ("Recorded fertiliser", result.inputs.fertilizer),
        ("Mean temperature", result.inputs.temperature),
        ("Mean humidity", result.inputs.humidity),
        ("Soil pH", result.inputs.soil_ph),
    ]
    input_rows = "".join(
        f"<tr><th>{safe(label)}</th><td>{safe(item.value)} {safe(item.unit)}</td></tr>"
        for label, item in values
    )
    status = "Synthetic demo" if result.data_status == "synthetic_demo" else "Real assessment"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Field Health Passport · {safe(result.assessment_id)}</title>
<style>
@page {{ size: A4; margin: 14mm; }}
* {{ box-sizing: border-box; }} body {{ font: 14px/1.45 Arial, sans-serif; color:#163A24; margin:0; }}
header {{ display:flex; justify-content:space-between; border-bottom:3px solid #1B5E20; padding-bottom:12px; }}
img {{ width:190px; height:auto; }} h1 {{ font-size:25px; margin:16px 0 4px; }} h2 {{ font-size:17px; margin:18px 0 8px; break-after:avoid; }}
.meta,.grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }} .card {{ border:1px solid #cdddcf; border-radius:10px; padding:12px; break-inside:avoid; }}
.hero {{ background:#f4faf4; margin:16px 0; }} .yield {{ font-size:34px; font-weight:800; }} table {{ width:100%; border-collapse:collapse; }} th,td {{ padding:7px; border-bottom:1px solid #dce9dd; text-align:left; }}
.risk {{ font-weight:800; }} .notice {{ border-left:4px solid #d99a00; padding:10px; background:#fff8e3; }}
.actions {{ margin-top:18px; }} button {{ padding:10px 16px; }}
@media print {{ .actions {{ display:none; }} body {{ font-size:12px; }} a {{ color:inherit; text-decoration:none; }} }}
</style></head><body>
<header><img src="/brand/mundasense_logo.png" alt="MundaSense AI"><div><strong>Field Health Passport</strong><br>{safe(status)}</div></header>
<h1>Maize field assessment</h1>
<div class="meta"><div><strong>Assessment ID</strong><br>{safe(result.assessment_id)}</div><div><strong>Created</strong><br>{safe(result.created_at)}</div><div><strong>District</strong><br>{safe(result.context.district or "Not recorded")}</div><div><strong>Field alias</strong><br>{safe(result.context.farm_reference or "Not recorded")}</div></div>
<section class="card hero"><div class="yield">{safe(result.prediction.yield_t_ha)} t/ha</div><div>Plausible range {safe(result.prediction.range_low_t_ha)}-{safe(result.prediction.range_high_t_ha)} t/ha</div><p class="risk">{safe(result.prediction.risk_label)} · {safe(result.prediction.confidence.band.title())} confidence</p></section>
<div class="grid"><section class="card"><h2>Recorded inputs</h2><table>{input_rows}</table></section><section class="card"><h2>Top model associations</h2><ol>{driver_rows}</ol></section></div>
<section class="card"><h2>Data-quality notes</h2><ul>{warning_rows}</ul></section>
<section class="card"><h2>Priority action</h2><strong>{safe(result.advisory.priority_action)}</strong><p>{safe(result.advisory.message)}</p><p><strong>Referral:</strong> {safe(result.advisory.referral_message or "Not required by the current rules.")}</p></section>
<section class="card"><h2>Technical record</h2><p>Model {safe(result.versions.model)} · Risk policy {safe(result.versions.risk_policy)} · Rules {safe(result.versions.rules)} · App {safe(result.versions.app)}</p></section>
<p class="notice"><strong>Responsible use:</strong> {safe(result.disclaimer)}</p>
<div class="actions"><button onclick="window.print()">Print or save as PDF</button></div>
</body></html>"""


def create_app(runtime_override: Runtime | None = None) -> FastAPI:
    app = FastAPI(
        title="MundaSense AI local API",
        version=APP_VERSION,
        description=(
            "Local delivery adapter for the maize-only MundaSense assessment service. "
            "The bundled model is synthetic and not field-validated."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "Idempotency-Key"],
    )
    app.mount("/brand", StaticFiles(directory=project_root() / "assets"), name="brand")

    def runtime() -> Runtime:
        return runtime_override or get_runtime()

    @app.middleware("http")
    async def limit_request_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 32_768:
            return Response(content="Request body too large", status_code=413)
        return await call_next(request)

    @app.get("/api/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        current = runtime()
        database_ok, database_detail = current.repository.database.readiness()
        required_dirs = [project_root() / name for name in ("data", "models", "reports", "docs")]
        missing_dirs = [path.name for path in required_dirs if not path.exists()]
        checks = {
            "model": HealthCheck(ok=True, detail=current.bundle["model_version"]),
            "rules": HealthCheck(ok=True, detail=current.engine.catalogue["catalogue_version"]),
            "locales": HealthCheck(
                ok=True,
                detail=(
                    "English + Shona "
                    f"({len(current.translator.missing_shona_keys())} fallback keys)"
                ),
            ),
            "database": HealthCheck(ok=database_ok, detail=database_detail),
            "directories": HealthCheck(
                ok=not missing_dirs,
                detail="present" if not missing_dirs else f"missing: {', '.join(missing_dirs)}",
            ),
        }
        ready = all(item.ok for item in checks.values())
        return HealthResponse(
            ready=ready,
            status="local_system_ready" if ready else "needs_attention",
            checks=checks,
            app_version=APP_VERSION,
            model_version=current.bundle.get("model_version"),
        )

    @app.get("/api/config", response_model=AppConfigResponse, tags=["system"])
    def config(language: Literal["en", "sn"] = "en") -> AppConfigResponse:
        current = runtime()
        return AppConfigResponse(
            features=_field_configs(current, language),
            locales=["en", "sn"],
            default_locale=current.config.default_locale,
            model_version=current.bundle["model_version"],
            app_version=APP_VERSION,
            extension_contact=current.config.extension_contact,
            demo_model=bool(current.bundle["is_synthetic"]),
        )

    @app.get("/api/demo-scenarios", response_model=list[DemoScenario], tags=["assessment"])
    def demo_scenarios() -> list[DemoScenario]:
        descriptions = {
            "balanced": "Plausible central-range inputs for the standard assessment journey.",
            "water_stress": "Lower rainfall and warmer conditions for exploring risk and drivers.",
            "unusual": "Processable outlying inputs for showing warnings and confidence safeguards.",
        }
        names = {
            "balanced": "Balanced conditions",
            "water_stress": "Water-stress conditions",
            "unusual": "Unusual data",
        }
        return [
            DemoScenario(
                id=key,
                name=names[key],
                description=descriptions[key],
                values=AssessmentCreate(**values, source="demo"),
            )
            for key, values in DEMO_SCENARIOS.items()
        ]

    @app.post(
        "/api/assessments",
        response_model=AssessmentResponse,
        status_code=201,
        tags=["assessment"],
    )
    def create_assessment(payload: AssessmentCreate) -> AssessmentResponse:
        current = runtime()
        try:
            result = current.service.assess(payload.to_domain(), persist=True)
        except AssessmentValidationError as exc:
            raise HTTPException(status_code=422, detail=_validation_detail(exc)) from exc
        return serialize_result(result, current.translator, payload.language)

    @app.get(
        "/api/assessments/export.csv",
        response_class=PlainTextResponse,
        tags=["history"],
    )
    def export_assessments(
        search: str | None = None,
        risk: str | None = None,
        confidence: str | None = None,
        district: str | None = None,
        referral: bool | None = None,
        data_status: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> PlainTextResponse:
        current = runtime()
        results = _filtered_results(
            current,
            search=search,
            risk=risk,
            confidence=confidence,
            district=district,
            referral=referral,
            data_status=data_status,
            from_date=from_date,
            to_date=to_date,
        )
        csv_text = current.repository.export_csv([item.assessment_id for item in results])
        return PlainTextResponse(
            csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=mundasense-assessments.csv"},
        )

    @app.get("/api/assessments", response_model=HistoryResponse, tags=["history"])
    def list_assessments(
        search: str | None = Query(default=None, max_length=120),
        risk: Literal["low", "moderate", "high"] | None = None,
        confidence: Literal["high", "medium", "low", "insufficient"] | None = None,
        district: str | None = Query(default=None, max_length=80),
        referral: bool | None = None,
        data_status: Literal["real", "synthetic_demo"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        sort: Literal["newest", "oldest", "highest_risk", "lowest_confidence"] = "newest",
    ) -> HistoryResponse:
        current = runtime()
        results = _filtered_results(
            current,
            search=search,
            risk=risk,
            confidence=confidence,
            district=district,
            referral=referral,
            data_status=data_status,
            from_date=from_date,
            to_date=to_date,
            sort=sort,
        )
        items = [history_item(item, current.translator) for item in results]
        districts = sorted(
            {
                item.validated_inputs.district
                for item in _all_results(current)
                if item.validated_inputs.district
            }
        )
        return HistoryResponse(items=items, total=len(items), districts=districts)

    @app.get(
        "/api/assessments/{assessment_id}/report",
        response_class=HTMLResponse,
        tags=["reporting"],
    )
    def assessment_report(assessment_id: str) -> HTMLResponse:
        current = runtime()
        result = current.repository.get(assessment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        serialized = serialize_result(result, current.translator, result.validated_inputs.language)
        return HTMLResponse(_report_html(serialized))

    @app.get(
        "/api/assessments/{assessment_id}",
        response_model=AssessmentResponse,
        tags=["history"],
    )
    def get_assessment(
        assessment_id: str, language: Literal["en", "sn"] | None = None
    ) -> AssessmentResponse:
        current = runtime()
        result = current.repository.get(assessment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return serialize_result(result, current.translator, language)

    @app.delete(
        "/api/assessments/{assessment_id}",
        status_code=204,
        tags=["history"],
    )
    def delete_assessment(assessment_id: str) -> Response:
        if not runtime().repository.delete(assessment_id):
            raise HTTPException(status_code=404, detail="Assessment not found")
        return Response(status_code=204)

    @app.post(
        "/api/scenarios/simulate",
        response_model=ScenarioSimulationResponse,
        tags=["scenario"],
    )
    def simulate_scenario(payload: ScenarioSimulationRequest) -> ScenarioSimulationResponse:
        current = runtime()
        baseline = current.repository.get(payload.baseline_assessment_id)
        if not baseline:
            raise HTTPException(status_code=404, detail="Baseline assessment not found")
        unknown = set(payload.overrides) - ALLOWED_FEATURES
        if unknown:
            raise HTTPException(
                status_code=422,
                detail={"code": "unknown_features", "features": sorted(unknown)},
            )
        request_values = baseline.validated_inputs.to_dict()
        request_values.update(payload.overrides)
        request_values.update({"source": "scenario", "language": payload.language})
        try:
            simulated = current.service.assess(request_values, persist=False)
        except AssessmentValidationError as exc:
            raise HTTPException(status_code=422, detail=_validation_detail(exc)) from exc
        base_response = serialize_result(baseline, current.translator, payload.language)
        scenario_response = serialize_result(simulated, current.translator, payload.language)
        return ScenarioSimulationResponse(
            baseline=base_response,
            scenario=scenario_response,
            delta=ScenarioDelta(
                yield_t_ha=round(simulated.predicted_yield_t_ha - baseline.predicted_yield_t_ha, 3),
                range_low_t_ha=round(
                    simulated.interval_lower_t_ha - baseline.interval_lower_t_ha, 3
                ),
                range_high_t_ha=round(
                    simulated.interval_upper_t_ha - baseline.interval_upper_t_ha, 3
                ),
                risk_changed=simulated.risk_code != baseline.risk_code,
                confidence_changed=simulated.confidence_code != baseline.confidence_code,
            ),
        )

    @app.get("/api/dashboard/summary", response_model=DashboardResponse, tags=["dashboard"])
    def dashboard_summary(
        risk: Literal["low", "moderate", "high"] | None = None,
        confidence: Literal["high", "medium", "low", "insufficient"] | None = None,
        district: str | None = Query(default=None, max_length=80),
        referral: bool | None = None,
        data_status: Literal["real", "synthetic_demo"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> DashboardResponse:
        current = runtime()
        results = _filtered_results(
            current,
            risk=risk,
            confidence=confidence,
            district=district,
            referral=referral,
            data_status=data_status,
            from_date=from_date,
            to_date=to_date,
        )
        risk_counts = Counter(item.risk_code for item in results)
        confidence_counts = Counter(item.confidence_code for item in results)
        day_counts = Counter(item.created_at[:10] for item in results)
        driver_counts = Counter(driver.feature for item in results for driver in item.top_drivers)
        district_yields: defaultdict[str, list[float]] = defaultdict(list)
        for item in results:
            if item.validated_inputs.district:
                district_yields[item.validated_inputs.district].append(item.predicted_yield_t_ha)
        priority = sorted(
            results,
            key=lambda item: (
                item.referral_required,
                item.risk_code == "high",
                item.confidence_code in {"low", "insufficient"},
                item.created_at,
            ),
            reverse=True,
        )
        return DashboardResponse(
            kpis=DashboardKpis(
                total_assessments=len(results),
                high_risk_assessments=risk_counts["high"],
                average_predicted_yield_t_ha=(
                    round(fmean(item.predicted_yield_t_ha for item in results), 3)
                    if results
                    else None
                ),
                low_confidence_assessments=sum(
                    item.confidence_code in {"low", "insufficient"} for item in results
                ),
                referrals_required=sum(item.referral_required for item in results),
            ),
            assessments_over_time=[
                CountPoint(label=label, count=count) for label, count in sorted(day_counts.items())
            ],
            risk_distribution=[
                CountPoint(label=label, count=risk_counts[label])
                for label in ("low", "moderate", "high")
            ],
            confidence_distribution=[
                CountPoint(label=label, count=confidence_counts[label])
                for label in ("high", "medium", "low", "insufficient")
            ],
            frequent_drivers=[
                CountPoint(label=label, count=count) for label, count in driver_counts.most_common()
            ],
            yield_by_district=[
                YieldPoint(
                    label=label,
                    average_yield_t_ha=round(fmean(values), 3),
                    sample_size=len(values),
                )
                for label, values in sorted(district_yields.items())
            ],
            priority_cases=[history_item(item, current.translator) for item in priority[:10]],
            contains_synthetic_demo=any(
                derive_data_status(item) == "synthetic_demo" for item in results
            ),
            small_sample=0 < len(results) < 10,
            active_filters={
                "risk": risk,
                "confidence": confidence,
                "district": district,
                "referral": referral,
                "data_status": data_status,
                "from_date": from_date.isoformat() if from_date else None,
                "to_date": to_date.isoformat() if to_date else None,
            },
        )

    @app.get("/api/model-card", response_model=ModelCardResponse, tags=["model"])
    def model_card(language: Literal["en", "sn"] = "en") -> ModelCardResponse:
        current = runtime()
        bundle = current.bundle
        metrics = bundle["metrics"]
        return ModelCardResponse(
            model_version=bundle["model_version"],
            status="Synthetic demonstration only — not field-validated",
            champion=bundle["training_config"]["champion"].replace("_", " ").title(),
            created_at=bundle["created_at"],
            explanation_method=bundle["explanation_method"],
            interval_method=bundle["residual_calibration"]["method"],
            metrics=[
                ModelMetric(label="Held-out MAE", value=metrics["mae_t_ha"], unit="t/ha"),
                ModelMetric(label="Held-out RMSE", value=metrics["rmse_t_ha"], unit="t/ha"),
                ModelMetric(label="Held-out R²", value=metrics["r2"]),
                ModelMetric(
                    label="Interval coverage",
                    value=metrics["interval_empirical_coverage"],
                    unit="proportion",
                ),
            ],
            features=_field_configs(current, language),
            limitations=[
                "All training and held-out evidence is deterministic synthetic data.",
                "The five inputs omit many agronomic and local field factors.",
                "Risk thresholds and confidence rules remain provisional.",
                "Driver values are model associations, not biological causes.",
                "The tool must not prescribe input doses or guarantee harvest outcomes.",
            ],
            training_ranges=bundle["training_ranges"],
        )

    frontend_dist = project_root() / "frontend" / "dist"
    if frontend_dist.exists():
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str) -> FileResponse:
            if path.startswith(("api/", "brand/")):
                raise HTTPException(status_code=404, detail="Not found")
            candidate = (frontend_dist / path).resolve()
            if frontend_dist.resolve() in candidate.parents and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


app = create_app()
