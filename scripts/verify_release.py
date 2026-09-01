from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mundasense.advisory.engine import AdvisoryEngine  # noqa: E402
from mundasense.config import AppConfig  # noqa: E402
from mundasense.data.demo_data import DEMO_SCENARIOS  # noqa: E402
from mundasense.health import readiness  # noqa: E402
from mundasense.i18n.translator import Translator  # noqa: E402
from mundasense.ml.registry import load_bundle  # noqa: E402
from mundasense.services.assessment_service import AssessmentService  # noqa: E402

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "requirements-lock.txt",
    "app.py",
    "assets/mundasense_logo.png",
    "data/sample/maize_demo.csv",
    "reports/metrics/evaluation.json",
    "reports/figures/actual_vs_predicted.png",
    "reports/figures/residuals.png",
    "docs/architecture.md",
    "docs/data_dictionary.md",
    "docs/data_sheet.md",
    "docs/model_card.md",
    "docs/advisory_rules.md",
    "docs/responsible_ai.md",
    "docs/testing.md",
    "docs/pilot_roadmap.md",
    "docs/threat_model.md",
    "docs/limitations.md",
    "docs/operational_notes.md",
]

CRITICAL_TRANSLATION_KEYS = {
    "app.title",
    "demo.banner",
    "risk.low",
    "risk.moderate",
    "risk.high",
    "confidence.high",
    "confidence.medium",
    "confidence.low",
    "result.referral",
    "result.disclaimer",
    "advice.verify.body",
    "advice.high_risk.body",
}


def main() -> None:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            failures.append(f"missing required file: {relative}")
    config = AppConfig.from_env()
    try:
        translator = Translator(config.locales_dir)
        missing_critical = sorted(CRITICAL_TRANSLATION_KEYS - set(translator.catalogues["en"]))
        if missing_critical:
            failures.append(f"English catalogue missing critical keys: {missing_critical}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"translation validation failed: {exc}")
    try:
        engine = AdvisoryEngine(config.rules_path)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"advisory catalogue failed: {exc}")
        engine = None
    try:
        bundle = load_bundle(config.model_path, trusted_directory=config.trusted_models_dir)
        required_metric_keys = {
            "mae_t_ha",
            "rmse_t_ha",
            "r2",
            "interval_empirical_coverage",
            "mean_interval_width_t_ha",
        }
        if not required_metric_keys.issubset(bundle["metrics"]):
            failures.append("model bundle lacks required held-out metrics")
        if bundle["training_config"]["champion"] == "naive_median":
            failures.append("naive baseline cannot be the released champion")
        if bundle["metrics"]["validation_mae_improvement_over_baseline"] <= 0:
            failures.append("released champion does not improve on the naive baseline")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"model bundle failed: {exc}")
        bundle = None
    if bundle and engine:
        service = AssessmentService(bundle=bundle, advisory_engine=engine)
        for name, payload in DEMO_SCENARIOS.items():
            try:
                result = service.assess(payload, persist=False)
                if len(result.top_drivers) != 3:
                    failures.append(f"scenario {name} did not return three drivers")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"scenario {name} failed: {exc}")
    health = readiness(config)
    if not health["ready"]:
        for name, check in health["checks"].items():
            if not check["ok"]:
                failures.append(f"readiness {name}: {check['detail']}")
    if failures:
        print("RELEASE VERIFICATION FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(
        json.dumps(
            {
                "status": "pass",
                "model_version": bundle["model_version"] if bundle else None,
                "scenarios_verified": list(DEMO_SCENARIOS),
                "readiness": health,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
