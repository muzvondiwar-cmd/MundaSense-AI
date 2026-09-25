from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mundasense.advisory.engine import AdvisoryEngine  # noqa: E402
from mundasense.config import AppConfig  # noqa: E402
from mundasense.data.demo_data import DEMO_SCENARIOS  # noqa: E402
from mundasense.ml.registry import load_bundle  # noqa: E402
from mundasense.services.assessment_service import AssessmentService  # noqa: E402
from mundasense.storage.assessment_repository import AssessmentRepository  # noqa: E402
from mundasense.storage.catalog_repository import CatalogRepository  # noqa: E402
from mundasense.storage.database import Database  # noqa: E402

SEED_VERSION = "hack4africa-2026-v1"

FARMS = [
    {
        "id": "10000000-0000-4000-8000-000000000001",
        "name": "Mhepo Demo Farm",
        "contact_name": "Demo Farmer A",
        "province": "Mashonaland East",
        "district": "Goromonzi",
        "ward": "12",
        "notes": "Synthetic demonstration farm; no real personal information.",
        "is_demo": True,
    },
    {
        "id": "10000000-0000-4000-8000-000000000002",
        "name": "Chiedza Demo Plot",
        "contact_name": "Demo Farmer B",
        "province": "Masvingo",
        "district": "Masvingo",
        "ward": "7",
        "notes": "Synthetic water-stress demonstration context.",
        "is_demo": True,
    },
    {
        "id": "10000000-0000-4000-8000-000000000003",
        "name": "Tariro Demo Farm",
        "contact_name": "Demo Farmer C",
        "province": "Midlands",
        "district": "Gokwe South",
        "ward": "4",
        "notes": "Synthetic extension-officer dashboard context.",
        "is_demo": True,
    },
]

FIELDS = [
    {
        "id": "20000000-0000-4000-8000-000000000001",
        "farm_id": FARMS[0]["id"],
        "name": "North Block",
        "size_hectares": 2.4,
        "maize_variety": "Demo medium-season variety",
        "planting_date": "2025-11-20",
        "season": "2025/26",
        "target_yield_t_ha": 4.0,
        "is_demo": True,
    },
    {
        "id": "20000000-0000-4000-8000-000000000002",
        "farm_id": FARMS[1]["id"],
        "name": "Dryland East",
        "size_hectares": 1.7,
        "maize_variety": "Demo early-maturing variety",
        "planting_date": "2025-12-03",
        "season": "2025/26",
        "target_yield_t_ha": 3.0,
        "is_demo": True,
    },
    {
        "id": "20000000-0000-4000-8000-000000000003",
        "farm_id": FARMS[2]["id"],
        "name": "River Field",
        "size_hectares": 3.1,
        "maize_variety": "Demo open-pollinated variety",
        "planting_date": "2025-11-28",
        "season": "2025/26",
        "target_yield_t_ha": 3.6,
        "is_demo": True,
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the fictional MundaSense demo dataset.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove demo assessments and rebuild the canonical seed; manual records are preserved.",
    )
    args = parser.parse_args()
    config = AppConfig.from_env()
    database = Database(config.database_path)
    repository = AssessmentRepository(database)
    catalog = CatalogRepository(database)
    if args.reset:
        removed = repository.delete_demo_records()
        catalog.delete_setting("demo_seed_version")
        print(f"Removed {removed} demo assessments; manual records were preserved.")
    if catalog.get_setting("demo_seed_version") == SEED_VERSION:
        print(f"Demonstration seed {SEED_VERSION} is already present; no duplicates created.")
        return

    for farm in FARMS:
        catalog.create_farm(farm)
    for field in FIELDS:
        catalog.create_field(field)

    service = AssessmentService(
        bundle=load_bundle(config.model_path, trusted_directory=config.trusted_models_dir),
        advisory_engine=AdvisoryEngine(config.rules_path),
        repository=repository,
    )
    sequence = [
        ("balanced", FIELDS[0], {}),
        ("water_stress", FIELDS[1], {}),
        ("unusual", FIELDS[2], {}),
        ("balanced", FIELDS[2], {"rainfall_mm": 610.0, "fertilizer_kg_ha": 95.0}),
        ("water_stress", FIELDS[1], {"rainfall_mm": 330.0, "temperature_c": 29.5}),
        ("balanced", FIELDS[0], {"rainfall_mm": 760.0, "soil_ph": 5.9}),
        ("water_stress", FIELDS[2], {"rainfall_mm": 410.0, "humidity_pct": 45.0}),
        ("balanced", FIELDS[0], {"fertilizer_kg_ha": 155.0, "temperature_c": 25.5}),
        ("unusual", FIELDS[1], {"rainfall_mm": 1280.0, "soil_ph": 8.6}),
    ]
    base_time = datetime.now(UTC).replace(microsecond=0) - timedelta(days=len(sequence) - 1)
    for index, (name, field, overrides) in enumerate(sequence):
        farm = next(item for item in FARMS if item["id"] == field["farm_id"])
        payload = {
            **DEMO_SCENARIOS[name],
            **overrides,
            "district": farm["district"],
            "farm_reference": field["name"],
            "source": "demo",
        }
        service.clock = lambda index=index: base_time + timedelta(days=index)
        result = service.assess(payload, persist=False)
        repository.save(
            result,
            idempotency_key=f"seed-{SEED_VERSION}-{index}",
            field_id=field["id"],
            sync_status="pending" if index == 1 else "synchronized",
        )
        print(
            f"{field['name']}: {result.predicted_yield_t_ha:.2f} t/ha, "
            f"{result.risk_code} risk, {result.confidence_code} confidence"
        )
    catalog.set_setting("demo_seed_version", SEED_VERSION)
    print(f"Seeded {len(FARMS)} demo farms, {len(FIELDS)} fields, and {len(sequence)} assessments.")


if __name__ == "__main__":
    main()
