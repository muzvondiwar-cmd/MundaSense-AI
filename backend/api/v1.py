from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import replace
from datetime import date
from statistics import fmean
from typing import Literal

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import ValidationError

from backend.dependencies import Runtime
from backend.schemas import (
    AppConfigResponse,
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
    ScenarioSimulationResponse,
    YieldPoint,
)
from backend.serializers import derive_data_status, history_item, serialize_result
from backend.v1_schemas import (
    AssessmentV1Create,
    FarmCreate,
    FarmResponse,
    FieldCreate,
    FieldResponse,
    InsightPoint,
    InsightsResponse,
    PredictionContract,
    ScenarioCompareRequest,
    SyncBatchRequest,
    SyncBatchResponse,
    SyncItemResult,
    YieldRange,
)
from mundasense.config import project_root
from mundasense.constants import APP_VERSION, FEATURE_SPEC
from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.schemas import AssessmentResult, AssessmentValidationError
from mundasense.storage.catalog_repository import CatalogRepository

ALLOWED_FEATURES = frozenset(FEATURE_SPEC)


def _catalog(runtime: Runtime) -> CatalogRepository:
    return runtime.catalog or CatalogRepository(runtime.repository.database)


def _features(runtime: Runtime, locale: str) -> list[FeatureConfig]:
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
    return [
        result
        for row in runtime.repository.list(limit=2_000)
        if (result := runtime.repository.get(row["id"]))
    ]


def _filtered_results(
    runtime: Runtime,
    *,
    search: str | None = None,
    risk: str | None = None,
    confidence: str | None = None,
    district: str | None = None,
    field: str | None = None,
    season: str | None = None,
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
            item
            for item in results
            if any(
                needle in value.casefold()
                for value in (
                    item.assessment_id,
                    item.validated_inputs.district,
                    item.validated_inputs.farm_reference,
                )
            )
        ]
    if field:
        needle = field.casefold()
        results = [
            item for item in results if needle in item.validated_inputs.farm_reference.casefold()
        ]
    if season:
        results = [item for item in results if item.validated_inputs.season == season]
    if referral is not None:
        results = [item for item in results if item.referral_required is referral]
    if data_status:
        results = [item for item in results if derive_data_status(item) == data_status]
    risk_rank = {"low": 0, "moderate": 1, "high": 2}
    confidence_rank = {"high": 0, "medium": 1, "low": 2, "insufficient": 3}
    if sort == "oldest":
        results.sort(key=lambda item: item.created_at)
    elif sort == "highest_risk":
        results.sort(key=lambda item: (risk_rank[item.risk_code], item.created_at), reverse=True)
    elif sort == "lowest_confidence":
        results.sort(
            key=lambda item: (confidence_rank[item.confidence_code], item.created_at), reverse=True
        )
    else:
        results.sort(key=lambda item: item.created_at, reverse=True)
    return results


def _prediction_contract(result: AssessmentResponse) -> PredictionContract:
    actions = [result.advisory.message] + [
        item.message for item in result.advisory.supporting_actions
    ]
    return PredictionContract(
        predicted_yield_t_ha=result.prediction.yield_t_ha,
        yield_range_t_ha=YieldRange(
            lower=result.prediction.range_low_t_ha, upper=result.prediction.range_high_t_ha
        ),
        risk_score=result.prediction.risk_score,
        risk_level=result.prediction.risk_band,
        confidence=result.prediction.confidence.band,
        confidence_explanation=result.prediction.confidence.method,
        top_drivers=result.drivers[:3],
        warnings=result.warnings,
        recommended_next_actions=actions,
        model_version=result.versions.model,
        is_demo_model=result.synthetic_model,
        full_result=result,
    )


def _retain_submission_context(
    result: AssessmentResult, payload: AssessmentV1Create
) -> AssessmentResult:
    return replace(
        result,
        technical_metadata={
            **result.technical_metadata,
            "submitted_context": payload.model_dump(mode="json"),
        },
    )


def build_v1_router(runtime_getter: Callable[[], Runtime]) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    @router.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        current = runtime_getter()
        database_ok, database_detail = current.repository.database.readiness()
        required = [project_root() / name for name in ("data", "models", "reports", "docs")]
        missing = [path.name for path in required if not path.exists()]
        checks = {
            "model": HealthCheck(ok=True, detail=current.bundle["model_version"]),
            "rules": HealthCheck(ok=True, detail=current.engine.catalogue["catalogue_version"]),
            "database": HealthCheck(ok=database_ok, detail=database_detail),
            "offline_assets": HealthCheck(
                ok=not missing, detail="ready" if not missing else f"missing: {', '.join(missing)}"
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

    @router.get("/config", response_model=AppConfigResponse, tags=["system"])
    def config(language: Literal["en", "sn"] = "en") -> AppConfigResponse:
        current = runtime_getter()
        return AppConfigResponse(
            features=_features(current, language),
            locales=["en", "sn"],
            default_locale=current.config.default_locale,
            model_version=current.bundle["model_version"],
            app_version=APP_VERSION,
            extension_contact=current.config.extension_contact,
            demo_model=bool(current.bundle["is_synthetic"]),
        )

    @router.get("/demo-scenarios", response_model=list[DemoScenario], tags=["assessment"])
    def demo_scenarios() -> list[DemoScenario]:
        descriptions = {
            "balanced": "Plausible rainfall and soil conditions with a lower-risk result.",
            "water_stress": "Low rainfall and warmer conditions with water-stress influence.",
            "unusual": "Outlying but processable inputs that trigger manual-review safeguards.",
        }
        names = {
            "balanced": "Balanced field",
            "water_stress": "Water-stressed field",
            "unusual": "Unusual data",
        }
        return [
            DemoScenario(
                id=key,
                name=names[key],
                description=descriptions[key],
                values={**values, "source": "demo"},
            )
            for key, values in DEMO_SCENARIOS.items()
        ]

    @router.delete("/demo-data", tags=["assessment"])
    def reset_demo_data() -> dict[str, int | str]:
        current = runtime_getter()
        removed = current.repository.delete_demo_records()
        _catalog(current).delete_setting("demo_seed_version")
        return {"status": "reset", "removed_assessments": removed}

    @router.get("/model/info", response_model=ModelCardResponse, tags=["model"])
    def model_info(language: Literal["en", "sn"] = "en") -> ModelCardResponse:
        current = runtime_getter()
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
            features=_features(current, language),
            limitations=[
                "All training and held-out evidence is deterministic synthetic data.",
                "The five model inputs omit many local agronomic factors.",
                "Risk thresholds and confidence rules remain provisional.",
                "Driver values are model associations, not causal proof.",
                "The prototype must not prescribe input doses or guarantee harvest outcomes.",
            ],
            training_ranges=bundle["training_ranges"],
        )

    @router.get("/farms", response_model=list[FarmResponse], tags=["farms"])
    def list_farms() -> list[dict]:
        return _catalog(runtime_getter()).list_farms()

    @router.post("/farms", response_model=FarmResponse, status_code=201, tags=["farms"])
    def create_farm(payload: FarmCreate) -> dict:
        return _catalog(runtime_getter()).create_farm(payload.model_dump(mode="json"))

    @router.get("/fields", response_model=list[FieldResponse], tags=["fields"])
    def list_fields(farm_id: str | None = Query(default=None, max_length=64)) -> list[dict]:
        return _catalog(runtime_getter()).list_fields(farm_id)

    @router.post("/fields", response_model=FieldResponse, status_code=201, tags=["fields"])
    def create_field(payload: FieldCreate) -> dict:
        try:
            return _catalog(runtime_getter()).create_field(payload.model_dump(mode="json"))
        except LookupError as exc:
            raise HTTPException(
                status_code=404, detail={"code": "farm_not_found", "message": str(exc)}
            ) from exc

    @router.post("/predictions", response_model=PredictionContract, tags=["prediction"])
    def predict(payload: AssessmentV1Create) -> PredictionContract:
        current = runtime_getter()
        try:
            result = current.service.assess(payload.legacy().to_domain(), persist=False)
        except AssessmentValidationError as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "assessment_validation_error", "errors": exc.errors},
            ) from exc
        return _prediction_contract(serialize_result(result, current.translator, payload.language))

    @router.post(
        "/assessments", response_model=AssessmentResponse, status_code=201, tags=["assessment"]
    )
    def create_assessment(
        payload: AssessmentV1Create,
        idempotency_header: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> AssessmentResponse:
        current = runtime_getter()
        key = idempotency_header or payload.idempotency_key
        if key and (existing := current.repository.get_by_idempotency_key(key)):
            return serialize_result(existing, current.translator, payload.language)
        if payload.field_id and not _catalog(current).get_field(payload.field_id):
            raise HTTPException(
                status_code=404,
                detail={"code": "field_not_found", "message": "Selected field was not found."},
            )
        try:
            result = current.service.assess(payload.legacy().to_domain(), persist=False)
        except AssessmentValidationError as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "assessment_validation_error", "errors": exc.errors},
            ) from exc
        result = _retain_submission_context(result, payload)
        current.repository.save(result, idempotency_key=key, field_id=payload.field_id)
        return serialize_result(result, current.translator, payload.language)

    @router.get("/assessments", response_model=HistoryResponse, tags=["assessment"])
    def list_assessments(
        search: str | None = Query(default=None, max_length=120),
        risk: Literal["low", "moderate", "high"] | None = None,
        confidence: Literal["high", "medium", "low", "insufficient"] | None = None,
        district: str | None = Query(default=None, max_length=80),
        field: str | None = Query(default=None, max_length=80),
        season: str | None = Query(default=None, max_length=30),
        referral: bool | None = None,
        data_status: Literal["real", "synthetic_demo"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        sort: Literal["newest", "oldest", "highest_risk", "lowest_confidence"] = "newest",
    ) -> HistoryResponse:
        current = runtime_getter()
        results = _filtered_results(
            current,
            search=search,
            risk=risk,
            confidence=confidence,
            district=district,
            field=field,
            season=season,
            referral=referral,
            data_status=data_status,
            from_date=from_date,
            to_date=to_date,
            sort=sort,
        )
        metadata = {row["id"]: row for row in current.repository.list(limit=2_000)}
        return HistoryResponse(
            items=[
                history_item(
                    item,
                    current.translator,
                    sync_status=metadata.get(item.assessment_id, {}).get(
                        "sync_status", "synchronized"
                    ),
                    archived=bool(metadata.get(item.assessment_id, {}).get("archived", False)),
                )
                for item in results
            ],
            total=len(results),
            districts=sorted(
                {
                    item.validated_inputs.district
                    for item in _all_results(current)
                    if item.validated_inputs.district
                }
            ),
        )

    @router.get(
        "/assessments/{assessment_id}", response_model=AssessmentResponse, tags=["assessment"]
    )
    def get_assessment(
        assessment_id: str, language: Literal["en", "sn"] | None = None
    ) -> AssessmentResponse:
        current = runtime_getter()
        result = current.repository.get(assessment_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail={"code": "assessment_not_found", "message": "Assessment not found."},
            )
        return serialize_result(result, current.translator, language)

    @router.patch("/assessments/{assessment_id}/archive", status_code=204, tags=["assessment"])
    def archive_assessment(assessment_id: str) -> None:
        if not runtime_getter().repository.archive(assessment_id):
            raise HTTPException(
                status_code=404,
                detail={"code": "assessment_not_found", "message": "Assessment not found."},
            )

    @router.post("/scenarios/compare", response_model=ScenarioSimulationResponse, tags=["scenario"])
    def compare_scenario(payload: ScenarioCompareRequest) -> ScenarioSimulationResponse:
        current = runtime_getter()
        baseline = current.repository.get(payload.baseline_assessment_id)
        if not baseline:
            raise HTTPException(
                status_code=404,
                detail={"code": "baseline_not_found", "message": "Baseline assessment not found."},
            )
        unknown = set(payload.overrides) - ALLOWED_FEATURES
        if unknown:
            raise HTTPException(
                status_code=422, detail={"code": "unknown_features", "features": sorted(unknown)}
            )
        request_values = baseline.validated_inputs.to_dict()
        request_values.update(payload.overrides)
        request_values.update({"source": "scenario", "language": payload.language})
        try:
            scenario = current.service.assess(request_values, persist=False)
        except AssessmentValidationError as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "assessment_validation_error", "errors": exc.errors},
            ) from exc
        baseline_response = serialize_result(baseline, current.translator, payload.language)
        scenario_response = serialize_result(scenario, current.translator, payload.language)
        return ScenarioSimulationResponse(
            baseline=baseline_response,
            scenario=scenario_response,
            delta=ScenarioDelta(
                yield_t_ha=round(scenario.predicted_yield_t_ha - baseline.predicted_yield_t_ha, 3),
                range_low_t_ha=round(
                    scenario.interval_lower_t_ha - baseline.interval_lower_t_ha, 3
                ),
                range_high_t_ha=round(
                    scenario.interval_upper_t_ha - baseline.interval_upper_t_ha, 3
                ),
                risk_changed=scenario.risk_code != baseline.risk_code,
                confidence_changed=scenario.confidence_code != baseline.confidence_code,
            ),
        )

    @router.get("/dashboard/summary", response_model=DashboardResponse, tags=["dashboard"])
    def dashboard_summary(
        province: str | None = Query(default=None, max_length=80),
        district: str | None = Query(default=None, max_length=80),
        field: str | None = Query(default=None, max_length=80),
        season: str | None = Query(default=None, max_length=30),
        risk: Literal["low", "moderate", "high"] | None = None,
        confidence: Literal["high", "medium", "low", "insufficient"] | None = None,
        referral: bool | None = None,
        data_status: Literal["real", "synthetic_demo"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> DashboardResponse:
        current = runtime_getter()
        results = _filtered_results(
            current,
            risk=risk,
            confidence=confidence,
            district=district,
            field=field,
            season=season,
            referral=referral,
            data_status=data_status,
            from_date=from_date,
            to_date=to_date,
        )
        if province:
            province_districts = {
                farm["district"]
                for farm in current.catalog.list_farms()
                if farm["province"].casefold() == province.casefold()
            }
            results = [
                item for item in results if item.validated_inputs.district in province_districts
            ]
        risk_counts = Counter(item.risk_code for item in results)
        confidence_counts = Counter(item.confidence_code for item in results)
        day_counts = Counter(item.created_at[:10] for item in results)
        day_yields: defaultdict[str, list[float]] = defaultdict(list)
        driver_counts = Counter(driver.feature for item in results for driver in item.top_drivers)
        district_yields: defaultdict[str, list[float]] = defaultdict(list)
        for item in results:
            day_yields[item.created_at[:10]].append(item.predicted_yield_t_ha)
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
        metadata = {row["id"]: row for row in current.repository.list(limit=2_000)}
        items = [
            history_item(
                item,
                current.translator,
                sync_status=metadata.get(item.assessment_id, {}).get("sync_status", "synchronized"),
            )
            for item in priority
        ]
        pending = len(current.repository.list(sync_status="pending", limit=2_000))
        return DashboardResponse(
            kpis=DashboardKpis(
                total_assessments=len(results),
                high_risk_assessments=risk_counts["high"],
                average_predicted_yield_t_ha=round(
                    fmean(item.predicted_yield_t_ha for item in results), 3
                )
                if results
                else None,
                low_confidence_assessments=sum(
                    item.confidence_code in {"low", "insufficient"} for item in results
                ),
                referrals_required=sum(item.referral_required for item in results),
                assessments_this_season=sum(
                    item.validated_inputs.season == "2025/26" for item in results
                ),
                awaiting_synchronization=pending,
            ),
            assessments_over_time=[
                CountPoint(label=key, count=value) for key, value in sorted(day_counts.items())
            ],
            yield_over_time=[
                YieldPoint(
                    label=key,
                    average_yield_t_ha=round(fmean(values), 3),
                    sample_size=len(values),
                )
                for key, values in sorted(day_yields.items())
            ],
            risk_distribution=[
                CountPoint(label=key, count=risk_counts[key]) for key in ("low", "moderate", "high")
            ],
            confidence_distribution=[
                CountPoint(label=key, count=confidence_counts[key])
                for key in ("high", "medium", "low", "insufficient")
            ],
            frequent_drivers=[
                CountPoint(label=key, count=value) for key, value in driver_counts.most_common()
            ],
            yield_by_district=[
                YieldPoint(
                    label=key, average_yield_t_ha=round(fmean(values), 3), sample_size=len(values)
                )
                for key, values in sorted(district_yields.items())
            ],
            priority_cases=items[:10],
            contains_synthetic_demo=any(
                derive_data_status(item) == "synthetic_demo" for item in results
            ),
            small_sample=0 < len(results) < 10,
            active_filters={
                "province": province,
                "district": district,
                "field": field,
                "season": season,
                "risk": risk,
                "data_status": data_status,
                "from_date": from_date.isoformat() if from_date else None,
                "to_date": to_date.isoformat() if to_date else None,
            },
            model_version=current.bundle["model_version"],
            recent_assessments=[
                history_item(
                    item,
                    current.translator,
                    sync_status=metadata.get(item.assessment_id, {}).get(
                        "sync_status", "synchronized"
                    ),
                )
                for item in results[:6]
            ],
            data_quality_alerts=[item for item in items if item.top_warning][:6],
        )

    @router.get("/insights", response_model=InsightsResponse, tags=["insights"])
    def insights() -> InsightsResponse:
        current = runtime_getter()
        results = _all_results(current)
        risks = Counter(item.risk_code for item in results)
        drivers = Counter(driver.feature for item in results for driver in item.top_drivers)
        versions = Counter(item.model_version for item in results)
        district_risks: defaultdict[str, list[int]] = defaultdict(list)
        input_keys = tuple(FEATURE_SPEC)
        input_values: defaultdict[str, list[float]] = defaultdict(list)
        for item in results:
            district_risks[item.validated_inputs.district or "Unspecified"].append(
                {"low": 0, "moderate": 1, "high": 2}[item.risk_code]
            )
            for key, value in item.validated_inputs.model_features().items():
                input_values[key].append(value)
        complete = sum(
            all(value is not None for value in item.validated_inputs.model_features().values())
            for item in results
        )
        return InsightsResponse(
            yield_over_time=[
                InsightPoint(label=item.created_at[:10], value=item.predicted_yield_t_ha)
                for item in sorted(results, key=lambda value: value.created_at)
            ],
            risk_distribution=[
                InsightPoint(label=key, value=value) for key, value in risks.items()
            ],
            risk_by_district=[
                InsightPoint(label=key, value=round(fmean(values), 2), sample_size=len(values))
                for key, values in sorted(district_risks.items())
            ],
            average_inputs={
                key: round(fmean(input_values[key]), 2) if input_values[key] else 0
                for key in input_keys
            },
            common_risk_drivers=[
                InsightPoint(label=key, value=value) for key, value in drivers.most_common()
            ],
            data_completeness_pct=round(100 * complete / len(results), 1) if results else 0,
            unusual_records=sum(bool(item.data_warnings) for item in results),
            model_versions=[
                InsightPoint(label=key, value=value) for key, value in versions.items()
            ],
            total_records=len(results),
            contains_demo_data=any(
                derive_data_status(item) == "synthetic_demo" for item in results
            ),
        )

    @router.post("/sync/batch", response_model=SyncBatchResponse, tags=["sync"])
    def sync_batch(payload: SyncBatchRequest) -> SyncBatchResponse:
        current = runtime_getter()
        catalog = _catalog(current)
        output: list[SyncItemResult] = []
        for item in payload.items:
            existing = catalog.get_sync_event(item.idempotency_key)
            if existing:
                output.append(
                    SyncItemResult(
                        idempotency_key=item.idempotency_key,
                        entity_type=item.entity_type,
                        entity_id=existing["entity_id"],
                        status="synchronized" if existing["status"] == "synchronized" else "failed",
                        duplicate=True,
                    )
                )
                continue
            try:
                if item.entity_type == "farm":
                    entity = catalog.create_farm(
                        {
                            **FarmCreate(**item.payload).model_dump(mode="json"),
                            "sync_status": "synchronized",
                        }
                    )
                    entity_id = entity["id"]
                elif item.entity_type == "field":
                    entity = catalog.create_field(
                        {
                            **FieldCreate(**item.payload).model_dump(mode="json"),
                            "sync_status": "synchronized",
                        }
                    )
                    entity_id = entity["id"]
                else:
                    request = AssessmentV1Create(**item.payload)
                    previous = current.repository.get_by_idempotency_key(item.idempotency_key)
                    if previous:
                        result = previous
                    else:
                        result = current.service.assess(request.legacy().to_domain(), persist=False)
                        result = _retain_submission_context(result, request)
                        current.repository.save(
                            result, idempotency_key=item.idempotency_key, field_id=request.field_id
                        )
                    entity_id = result.assessment_id
                response = {"entity_id": entity_id, "status": "synchronized"}
                catalog.record_sync_event(
                    idempotency_key=item.idempotency_key,
                    entity_type=item.entity_type,
                    entity_id=entity_id,
                    status="synchronized",
                    request=item.payload,
                    response=response,
                )
                output.append(
                    SyncItemResult(
                        idempotency_key=item.idempotency_key,
                        entity_type=item.entity_type,
                        entity_id=entity_id,
                        status="synchronized",
                    )
                )
            except (AssessmentValidationError, LookupError, ValidationError, ValueError) as exc:
                output.append(
                    SyncItemResult(
                        idempotency_key=item.idempotency_key,
                        entity_type=item.entity_type,
                        entity_id=str(item.payload.get("id", "")),
                        status="failed",
                        error=str(exc),
                    )
                )
        return SyncBatchResponse(
            items=output,
            synchronized=sum(item.status == "synchronized" for item in output),
            failed=sum(item.status == "failed" for item in output),
        )

    return router
