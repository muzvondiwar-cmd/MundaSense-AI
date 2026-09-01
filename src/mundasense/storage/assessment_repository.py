from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from datetime import date
from typing import Any

from mundasense.constants import APP_VERSION
from mundasense.schemas import AssessmentRequest, AssessmentResult
from mundasense.storage.database import Database


def neutralise_formula(value: Any) -> Any:
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


class AssessmentRepository:
    def __init__(self, database: Database):
        self.database = database
        self.database.initialise()

    def save(self, result: AssessmentResult) -> None:
        payload = result.to_dict()
        inputs = result.validated_inputs.to_dict()
        values = (
            result.assessment_id,
            result.created_at,
            inputs["crop"],
            inputs["district"],
            inputs["farm_reference"],
            json.dumps(inputs, ensure_ascii=False, sort_keys=True),
            result.predicted_yield_t_ha,
            result.interval_lower_t_ha,
            result.interval_upper_t_ha,
            result.risk_code,
            result.confidence_code,
            json.dumps([asdict(item) for item in result.data_warnings], ensure_ascii=False),
            json.dumps([asdict(item) for item in result.top_drivers], ensure_ascii=False),
            json.dumps([asdict(item) for item in result.advisories], ensure_ascii=False),
            int(result.referral_required),
            result.model_version,
            result.rules_version,
            int(result.is_synthetic_model),
            APP_VERSION,
            json.dumps(payload, ensure_ascii=False, sort_keys=True),
        )
        sql = """
        INSERT INTO assessments (
            id, created_at, crop, district, farm_reference, inputs_json,
            predicted_yield_t_ha, interval_lower_t_ha, interval_upper_t_ha,
            risk_code, confidence_code, warnings_json, drivers_json, advisories_json,
            referral_required, model_version, rules_version, is_synthetic_model,
            app_version, result_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.database.connect() as connection:
            connection.execute(sql, values)
            connection.commit()

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
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT result_json FROM assessments WHERE id = ?", (assessment_id,)
            ).fetchone()
        if row is None:
            return None
        return self._hydrate(json.loads(row["result_json"]))

    def list(
        self,
        *,
        risk: str | None = None,
        confidence: str | None = None,
        district: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if risk:
            clauses.append("risk_code = ?")
            params.append(risk)
        if confidence:
            clauses.append("confidence_code = ?")
            params.append(confidence)
        if district:
            clauses.append("district = ?")
            params.append(district)
        if from_date:
            clauses.append("date(created_at) >= date(?)")
            params.append(from_date.isoformat())
        if to_date:
            clauses.append("date(created_at) <= date(?)")
            params.append(to_date.isoformat())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""SELECT id, created_at, district, farm_reference,
            predicted_yield_t_ha, interval_lower_t_ha, interval_upper_t_ha,
            risk_code, confidence_code, referral_required, model_version,
            is_synthetic_model FROM assessments {where}
            ORDER BY created_at DESC LIMIT ?"""
        params.append(min(max(limit, 1), 2_000))
        with self.database.connect() as connection:
            return [dict(row) for row in connection.execute(sql, params).fetchall()]

    def delete(self, assessment_id: str) -> bool:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
            connection.commit()
            return cursor.rowcount == 1

    def export_csv(self, assessment_ids: list[str] | None = None) -> str:
        sql = "SELECT result_json FROM assessments"
        params: list[Any] = []
        if assessment_ids:
            placeholders = ",".join("?" for _ in assessment_ids)
            sql += f" WHERE id IN ({placeholders})"
            params.extend(assessment_ids)
        sql += " ORDER BY created_at DESC"
        with self.database.connect() as connection:
            payloads = [json.loads(row["result_json"]) for row in connection.execute(sql, params)]
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
            "model_version",
            "rules_version",
            "is_synthetic_model",
        ]
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for payload in payloads:
            inputs = payload["validated_inputs"]
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
                "model_version": payload["model_version"],
                "rules_version": payload["rules_version"],
                "is_synthetic_model": payload["is_synthetic_model"],
            }
            writer.writerow({key: neutralise_formula(value) for key, value in row.items()})
        return stream.getvalue()
