from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from datetime import date
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, func, select

from mundasense.advisory.policy import HIGH_RISK_BELOW_T_HA, MODERATE_RISK_BELOW_T_HA
from mundasense.constants import APP_VERSION
from mundasense.schemas import AssessmentRequest, AssessmentResult
from mundasense.storage.database import Database
from mundasense.storage.models import AssessmentRecord, PredictionRecord


def neutralise_formula(value: Any) -> Any:
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def risk_score_for_yield(predicted_yield_t_ha: float) -> float:
    """Map provisional yield thresholds to a transparent 0-100 concern score."""
    if predicted_yield_t_ha <= HIGH_RISK_BELOW_T_HA:
        score = 70 + 30 * (HIGH_RISK_BELOW_T_HA - predicted_yield_t_ha) / HIGH_RISK_BELOW_T_HA
    elif predicted_yield_t_ha < MODERATE_RISK_BELOW_T_HA:
        width = MODERATE_RISK_BELOW_T_HA - HIGH_RISK_BELOW_T_HA
        score = 40 + 30 * (MODERATE_RISK_BELOW_T_HA - predicted_yield_t_ha) / width
    else:
        score = 40 * max(0.0, 1 - (predicted_yield_t_ha - MODERATE_RISK_BELOW_T_HA) / 3.5)
    return round(min(100.0, max(0.0, score)), 1)


class AssessmentRepository:
    def __init__(self, database: Database):
        self.database = database
        self.database.initialise()

    def save(
        self,
        result: AssessmentResult,
        *,
        idempotency_key: str | None = None,
        field_id: str | None = None,
        sync_status: str = "synchronized",
    ) -> AssessmentResult:
        if idempotency_key:
            existing = self.get_by_idempotency_key(idempotency_key)
            if existing:
                return existing
        payload = result.to_dict()
        inputs = result.validated_inputs.to_dict()
        with self.database.session() as session:
            session.add(
                AssessmentRecord(
                    id=result.assessment_id,
                    created_at=result.created_at,
                    updated_at=result.created_at,
                    crop=inputs["crop"],
                    district=inputs["district"],
                    farm_reference=inputs["farm_reference"],
                    inputs_json=json.dumps(inputs, ensure_ascii=False, sort_keys=True),
                    predicted_yield_t_ha=result.predicted_yield_t_ha,
                    interval_lower_t_ha=result.interval_lower_t_ha,
                    interval_upper_t_ha=result.interval_upper_t_ha,
                    risk_code=result.risk_code,
                    confidence_code=result.confidence_code,
                    warnings_json=json.dumps(
                        [asdict(item) for item in result.data_warnings], ensure_ascii=False
                    ),
                    drivers_json=json.dumps(
                        [asdict(item) for item in result.top_drivers], ensure_ascii=False
                    ),
                    advisories_json=json.dumps(
                        [asdict(item) for item in result.advisories], ensure_ascii=False
                    ),
                    referral_required=result.referral_required,
                    model_version=result.model_version,
                    rules_version=result.rules_version,
                    is_synthetic_model=result.is_synthetic_model,
                    app_version=APP_VERSION,
                    result_json=json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    sync_status=sync_status,
                    idempotency_key=idempotency_key,
                    archived=False,
                    field_id=field_id,
                )
            )
            session.add(
                PredictionRecord(
                    id=str(uuid4()),
                    assessment_id=result.assessment_id,
                    prediction_timestamp=result.created_at,
                    predicted_yield_t_ha=result.predicted_yield_t_ha,
                    lower_yield_t_ha=result.interval_lower_t_ha,
                    upper_yield_t_ha=result.interval_upper_t_ha,
                    risk_score=risk_score_for_yield(result.predicted_yield_t_ha),
                    risk_level=result.risk_code,
                    confidence=result.confidence_code,
                    drivers_json=json.dumps(
                        [asdict(item) for item in result.top_drivers], ensure_ascii=False
                    ),
                    warnings_json=json.dumps(
                        [asdict(item) for item in result.data_warnings], ensure_ascii=False
                    ),
                    recommendations_json=json.dumps(
                        [asdict(item) for item in result.advisories], ensure_ascii=False
                    ),
                    model_version=result.model_version,
                    is_demo_model=result.is_synthetic_model,
                )
            )
        return result

    @staticmethod
    def _hydrate(payload: dict[str, Any]) -> AssessmentResult:
        from mundasense.schemas import Advisory, DataWarning, PredictionDriver

        return AssessmentResult(
            **{
                **payload,
                "validated_inputs": AssessmentRequest(**payload["validated_inputs"]),
                "top_drivers": tuple(PredictionDriver(**item) for item in payload["top_drivers"]),
                "data_warnings": tuple(DataWarning(**item) for item in payload["data_warnings"]),
                "advisories": tuple(Advisory(**item) for item in payload["advisories"]),
            }
        )

    def get(self, assessment_id: str) -> AssessmentResult | None:
        with self.database.session() as session:
            payload = session.scalar(
                select(AssessmentRecord.result_json).where(AssessmentRecord.id == assessment_id)
            )
        return self._hydrate(json.loads(payload)) if payload else None

    def get_by_idempotency_key(self, key: str) -> AssessmentResult | None:
        with self.database.session() as session:
            payload = session.scalar(
                select(AssessmentRecord.result_json).where(AssessmentRecord.idempotency_key == key)
            )
        return self._hydrate(json.loads(payload)) if payload else None

    def list(
        self,
        *,
        risk: str | None = None,
        confidence: str | None = None,
        district: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        sync_status: str | None = None,
        include_archived: bool = False,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        statement = select(AssessmentRecord)
        if not include_archived:
            statement = statement.where(AssessmentRecord.archived.is_(False))
        if risk:
            statement = statement.where(AssessmentRecord.risk_code == risk)
        if confidence:
            statement = statement.where(AssessmentRecord.confidence_code == confidence)
        if district:
            statement = statement.where(AssessmentRecord.district == district)
        if from_date:
            statement = statement.where(
                func.date(AssessmentRecord.created_at) >= from_date.isoformat()
            )
        if to_date:
            statement = statement.where(
                func.date(AssessmentRecord.created_at) <= to_date.isoformat()
            )
        if sync_status:
            statement = statement.where(AssessmentRecord.sync_status == sync_status)
        statement = statement.order_by(AssessmentRecord.created_at.desc()).limit(
            min(max(limit, 1), 2_000)
        )
        with self.database.session() as session:
            rows = session.scalars(statement).all()
            return [
                {
                    "id": row.id,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                    "district": row.district,
                    "farm_reference": row.farm_reference,
                    "predicted_yield_t_ha": row.predicted_yield_t_ha,
                    "interval_lower_t_ha": row.interval_lower_t_ha,
                    "interval_upper_t_ha": row.interval_upper_t_ha,
                    "risk_code": row.risk_code,
                    "confidence_code": row.confidence_code,
                    "referral_required": row.referral_required,
                    "model_version": row.model_version,
                    "is_synthetic_model": row.is_synthetic_model,
                    "sync_status": row.sync_status,
                    "archived": row.archived,
                    "field_id": row.field_id,
                }
                for row in rows
            ]

    def archive(self, assessment_id: str) -> bool:
        with self.database.session() as session:
            record = session.get(AssessmentRecord, assessment_id)
            if not record:
                return False
            record.archived = True
            record.updated_at = record.created_at
            return True

    def delete(self, assessment_id: str) -> bool:
        with self.database.session() as session:
            record = session.get(AssessmentRecord, assessment_id)
            if not record:
                return False
            session.delete(record)
            return True

    def delete_demo_records(self) -> int:
        with self.database.session() as session:
            records = session.scalars(select(AssessmentRecord)).all()
            demo_records = [
                record
                for record in records
                if json.loads(record.inputs_json).get("source") in {"demo", "scenario"}
            ]
            ids = [record.id for record in demo_records]
            if ids:
                session.execute(
                    delete(PredictionRecord).where(PredictionRecord.assessment_id.in_(ids))
                )
                session.execute(delete(AssessmentRecord).where(AssessmentRecord.id.in_(ids)))
            return len(demo_records)

    def export_csv(self, assessment_ids: list[str] | None = None) -> str:
        statement = select(AssessmentRecord.result_json).order_by(
            AssessmentRecord.created_at.desc()
        )
        if assessment_ids is not None:
            statement = statement.where(AssessmentRecord.id.in_(assessment_ids or ["__none__"]))
        with self.database.session() as session:
            payloads = [json.loads(value) for value in session.scalars(statement).all()]
        columns = [
            "assessment_id",
            "created_at",
            "district",
            "farm_reference",
            "rainfall_mm",
            "fertilizer_kg_ha",
            "temperature_c",
            "humidity_pct",
            "soil_ph",
            "predicted_yield_t_ha",
            "interval_lower_t_ha",
            "interval_upper_t_ha",
            "risk_code",
            "confidence_code",
            "warning_codes",
            "advisory_rule_ids",
            "referral_required",
            "source",
            "data_status",
            "model_version",
            "rules_version",
            "is_synthetic_model",
        ]
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for payload in payloads:
            inputs = payload["validated_inputs"]
            source = inputs.get("source") or (
                "demo"
                if str(inputs.get("farm_reference", "")).lower().startswith("demo")
                else "manual"
            )
            data_status = payload.get("data_status") or (
                "synthetic_demo" if source in {"demo", "scenario"} else "real"
            )
            row = {
                "assessment_id": payload["assessment_id"],
                "created_at": payload["created_at"],
                "district": inputs["district"],
                "farm_reference": inputs["farm_reference"],
                **{
                    key: inputs[key]
                    for key in (
                        "rainfall_mm",
                        "fertilizer_kg_ha",
                        "temperature_c",
                        "humidity_pct",
                        "soil_ph",
                    )
                },
                "predicted_yield_t_ha": payload["predicted_yield_t_ha"],
                "interval_lower_t_ha": payload["interval_lower_t_ha"],
                "interval_upper_t_ha": payload["interval_upper_t_ha"],
                "risk_code": payload["risk_code"],
                "confidence_code": payload["confidence_code"],
                "warning_codes": ";".join(item["code"] for item in payload["data_warnings"]),
                "advisory_rule_ids": ";".join(item["rule_id"] for item in payload["advisories"]),
                "referral_required": payload["referral_required"],
                "source": source,
                "data_status": data_status,
                "model_version": payload["model_version"],
                "rules_version": payload["rules_version"],
                "is_synthetic_model": payload["is_synthetic_model"],
            }
            writer.writerow({key: neutralise_formula(value) for key, value in row.items()})
        return stream.getvalue()
