from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mundasense.constants import RULES_VERSION
from mundasense.schemas import Advisory, ConfidenceCode, DataWarning, RiskCode, RuleCatalogueError

REQUIRED_RULE_FIELDS = {
    "id",
    "title_key",
    "message_key",
    "priority",
    "trigger",
    "rationale",
    "review_status",
    "locale_applicability",
    "referral_required",
    "effective_date",
}


class AdvisoryEngine:
    def __init__(self, catalogue_path: Path):
        self.catalogue_path = catalogue_path
        self.catalogue = self._load()

    def _load(self) -> dict[str, Any]:
        try:
            payload = yaml.safe_load(self.catalogue_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise RuleCatalogueError(f"Could not load advisory rules: {exc}") from exc
        if not isinstance(payload, dict) or payload.get("catalogue_version") != RULES_VERSION:
            raise RuleCatalogueError("Advisory catalogue version is missing or incompatible.")
        rules = payload.get("rules")
        if not isinstance(rules, list) or not rules:
            raise RuleCatalogueError("Advisory catalogue must contain at least one rule.")
        identifiers: set[str] = set()
        for rule in rules:
            if not isinstance(rule, dict) or not REQUIRED_RULE_FIELDS.issubset(rule):
                raise RuleCatalogueError("Advisory rule is missing required fields.")
            if rule["id"] in identifiers:
                raise RuleCatalogueError(f"Duplicate advisory rule id: {rule['id']}")
            identifiers.add(rule["id"])
        return payload

    @staticmethod
    def _matches(
        trigger: str,
        *,
        inputs: dict[str, float],
        risk: RiskCode,
        confidence: ConfidenceCode,
        warnings: tuple[DataWarning, ...],
    ) -> bool:
        if trigger == "always":
            return True
        if trigger == "severe_warning":
            return any(item.severity == "severe" for item in warnings)
        if trigger == "low_confidence":
            return confidence in {"low", "insufficient"}
        if trigger == "high_risk":
            return risk == "high"
        if trigger == "possible_water_stress":
            return inputs["rainfall_mm"] < 400 or inputs["temperature_c"] > 30
        if trigger == "unusual_soil_ph":
            return inputs["soil_ph"] < 5.3 or inputs["soil_ph"] > 7.4
        return False

    def evaluate(
        self,
        *,
        inputs: dict[str, float],
        risk: RiskCode,
        confidence: ConfidenceCode,
        warnings: tuple[DataWarning, ...],
    ) -> tuple[Advisory, ...]:
        matched = [
            rule
            for rule in self.catalogue["rules"]
            if self._matches(
                rule["trigger"],
                inputs=inputs,
                risk=risk,
                confidence=confidence,
                warnings=warnings,
            )
        ]
        matched.sort(key=lambda rule: (-int(rule["priority"]), rule["id"]))
        selected = matched[:3]
        return tuple(
            Advisory(
                rule_id=rule["id"],
                priority=int(rule["priority"]),
                title_key=rule["title_key"],
                message_key=rule["message_key"],
                rationale=rule["rationale"],
                referral_required=bool(rule["referral_required"]),
                review_status=rule["review_status"],
            )
            for rule in selected
        )
