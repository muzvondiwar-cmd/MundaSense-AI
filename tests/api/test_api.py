from __future__ import annotations

from fastapi.testclient import TestClient

from backend.dependencies import Runtime
from backend.main import create_app
from mundasense.config import AppConfig, project_root
from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.i18n.translator import Translator


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
    )
    return TestClient(create_app(runtime))


def payload(name: str = "balanced", **overrides):
    return {**DEMO_SCENARIOS[name], "source": "demo", "language": "en", **overrides}


def test_health_config_and_explicit_cors(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["ready"] is True
    config = client.get("/api/config")
    assert config.status_code == 200
    assert [item["key"] for item in config.json()["features"]] == [
        "rainfall_mm",
        "fertilizer_kg_ha",
        "temperature_c",
        "humidity_pct",
        "soil_ph",
    ]
    cors = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert cors.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_create_retrieve_and_list_immutable_snapshot(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    created = client.post("/api/assessments", json=payload())
    assert created.status_code == 201
    body = created.json()
    assert body["context"]["crop"] == "maize"
    assert body["data_status"] == "synthetic_demo"
    assert len(body["drivers"]) == 3
    assessment_id = body["assessment_id"]
    reopened = client.get(f"/api/assessments/{assessment_id}")
    assert reopened.json() == body
    history = client.get("/api/assessments", params={"data_status": "synthetic_demo"})
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["assessment_id"] == assessment_id


def test_invalid_value_returns_field_specific_422(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    response = client.post("/api/assessments", json=payload(rainfall_mm=-1))
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "rainfall_mm"


def test_unusual_data_keeps_warnings_and_low_confidence(
    service, repository, trained_bundle
) -> None:
    client = make_client(service, repository, trained_bundle)
    response = client.post("/api/assessments", json=payload("unusual"))
    assert response.status_code == 201
    body = response.json()
    assert body["warnings"]
    assert body["prediction"]["confidence"]["band"] in {"low", "insufficient"}
    assert body["advisory"]["referral_required"] is True


def test_scenario_simulation_does_not_persist(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    baseline = client.post("/api/assessments", json=payload()).json()
    before = len(repository.list())
    response = client.post(
        "/api/scenarios/simulate",
        json={
            "baseline_assessment_id": baseline["assessment_id"],
            "overrides": {"rainfall_mm": 300},
            "language": "en",
        },
    )
    assert response.status_code == 200
    assert response.json()["persisted"] is False
    assert response.json()["scenario"]["inputs"]["rainfall"]["value"] == 300
    assert len(repository.list()) == before


def test_dashboard_uses_persisted_records_and_filters(service, repository, trained_bundle) -> None:
    client = make_client(service, repository, trained_bundle)
    client.post("/api/assessments", json=payload("balanced"))
    unusual = client.post("/api/assessments", json=payload("unusual")).json()
    dashboard = client.get("/api/dashboard/summary", params={"risk": "high"})
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["kpis"]["total_assessments"] == 1
    assert body["priority_cases"][0]["assessment_id"] == unusual["assessment_id"]
    assert body["contains_synthetic_demo"] is True


def test_export_neutralises_formulas_and_report_escapes_html(
    service, repository, trained_bundle
) -> None:
    client = make_client(service, repository, trained_bundle)
    created = client.post(
        "/api/assessments",
        json=payload(source="manual", farm_reference="=2+2", district="<script>x</script>"),
    ).json()
    export = client.get("/api/assessments/export.csv")
    assert export.status_code == 200
    assert "'=2+2" in export.text
    assert "source,data_status,model_version" in export.text

    empty_export = client.get("/api/assessments/export.csv", params={"search": "no-such-farm"})
    assert empty_export.status_code == 200
    assert len(empty_export.text.strip().splitlines()) == 1

    report = client.get(f"/api/assessments/{created['assessment_id']}/report")
    assert report.status_code == 200
    assert "<script>x</script>" not in report.text
    assert "&lt;script&gt;x&lt;/script&gt;" in report.text
