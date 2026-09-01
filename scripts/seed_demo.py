from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mundasense.advisory.engine import AdvisoryEngine  # noqa: E402
from mundasense.config import AppConfig  # noqa: E402
from mundasense.data.demo_data import DEMO_SCENARIOS  # noqa: E402
from mundasense.ml.registry import load_bundle  # noqa: E402
from mundasense.services.assessment_service import AssessmentService  # noqa: E402
from mundasense.storage.assessment_repository import AssessmentRepository  # noqa: E402
from mundasense.storage.database import Database  # noqa: E402


def main() -> None:
    config = AppConfig.from_env()
    service = AssessmentService(
        bundle=load_bundle(config.model_path, trusted_directory=config.trusted_models_dir),
        advisory_engine=AdvisoryEngine(config.rules_path),
        repository=AssessmentRepository(Database(config.database_path)),
    )
    for name, payload in DEMO_SCENARIOS.items():
        result = service.assess(payload)
        print(
            f"{name}: {result.predicted_yield_t_ha:.2f} t/ha, "
            f"{result.risk_code} risk, {result.confidence_code} confidence, "
            f"referral={result.referral_required}"
        )


if __name__ == "__main__":
    main()
