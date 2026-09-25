from __future__ import annotations

from fastapi.testclient import TestClient

from backend.dependencies import Runtime
from backend.main import create_app
from mundasense.config import AppConfig, project_root
from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.i18n.translator import Translator
from mundasense.storage.catalog_repository import CatalogRepository


def make_client(service, repository, trained_bundle) -> TestClient:
    root = project_root()
    config = AppConfig(
        data_path=root / "data" / "sample" / "maize_demo.csv",
        model_path=root / "models" / "mundasense_demo_v1.joblib",
        database_path=repository.database.path,
        default_locale="en",
        random_seed=42,
        log_level="INFO",
        demo_banner=True,
        extension_contact="Contact your local agricultural extension office.",
    )
    runtime = Runtime(
        config=config,
        translator=Translator(config.locales_dir),
        bundle=trained_bundle,
        repository=repository,
        engine=service.advisory_engine,
        service=service,
        catalog=CatalogRepository(repository.database),
    )
    return TestClient(create_app(runtime))


def assessment_payload(**overrides):
    return {
        **DEMO_SCENARIOS["balanced"],
        "source": "demo",
        "language": "en",
        **overrides,
    }


def test_v1_farm_field_prediction_and_assessment_flow(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    farm = client.post(
        "/api/v1/farms",
        json={
            "name": "Test demo farm",
            "contact_name": "Demo contact",
            "province": "Mashonaland East",
            "district": "Goromonzi",
            "ward": "12",
            "latitude": None,
            "longitude": None,
            "notes": "Synthetic test record",
        },
    )
    assert farm.status_code == 201
    field = client.post(
        "/api/v1/fields",
        json={
            "farm_id": farm.json()["id"],
            "name": "North field",
            "size_hectares": 2.5,
            "maize_variety": "Demo variety",
            "planting_date": "2025-11-20",
            "season": "2025/26",
            "target_yield_t_ha": 4.0,
            "notes": "",
        },
    )
    assert field.status_code == 201
    prediction = client.post(
        "/api/v1/predictions",
        json=assessment_payload(field_id=field.json()["id"]),
    )
    assert prediction.status_code == 200
    assert 0 <= prediction.json()["risk_score"] <= 100
    assert len(prediction.json()["top_drivers"]) == 3

    payload = assessment_payload(field_id=field.json()["id"])
    first = client.post(
        "/api/v1/assessments",
        json=payload,
        headers={"Idempotency-Key": "test-create-assessment-key"},
    )
    second = client.post(
        "/api/v1/assessments",
        json=payload,
        headers={"Idempotency-Key": "test-create-assessment-key"},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["assessment_id"] == second.json()["assessment_id"]


def test_v1_sync_batch_is_idempotent(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    request = {
        "items": [
            {
                "entity_type": "assessment",
                "idempotency_key": "offline-balanced-assessment",
                "payload": assessment_payload(),
            }
        ]
    }
    first = client.post("/api/v1/sync/batch", json=request)
    second = client.post("/api/v1/sync/batch", json=request)
    assert first.status_code == 200
    assert first.json()["synchronized"] == 1
    assert second.json()["items"][0]["duplicate"] is True
    assert first.json()["items"][0]["entity_id"] == second.json()["items"][0]["entity_id"]


def test_v1_insights_dashboard_and_error_envelope(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    client.post("/api/v1/assessments", json=assessment_payload())
    dashboard = client.get("/api/v1/dashboard/summary")
    assert dashboard.status_code == 200
    assert dashboard.json()["model_version"]
    assert dashboard.json()["recent_assessments"]
    insights = client.get("/api/v1/insights")
    assert insights.status_code == 200
    assert insights.json()["total_records"] == 1
    invalid = client.post("/api/v1/predictions", json=assessment_payload(rainfall_mm=-1))
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "request_validation_error"
