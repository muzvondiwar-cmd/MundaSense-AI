from __future__ import annotations

from pathlib import Path

import pytest

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.config import project_root
from mundasense.data.demo_data import write_demo_data
from mundasense.ml.train import train_model
from mundasense.services.assessment_service import AssessmentService
from mundasense.storage.assessment_repository import AssessmentRepository
from mundasense.storage.database import Database


@pytest.fixture(scope="session")
def trained_bundle(tmp_path_factory):
    root = tmp_path_factory.mktemp("trained")
    data_path = root / "maize_demo.csv"
    model_path = root / "models" / "demo.joblib"
    write_demo_data(data_path, rows=360, seed=42)
    return train_model(
        data_path,
        model_path,
        root / "metrics",
        root / "figures",
        seed=42,
    )


@pytest.fixture
def repository(tmp_path: Path) -> AssessmentRepository:
    return AssessmentRepository(Database(tmp_path / "history.sqlite3"))


@pytest.fixture
def service(trained_bundle, repository) -> AssessmentService:
    return AssessmentService(
        bundle=trained_bundle,
        advisory_engine=AdvisoryEngine(
            project_root() / "src" / "mundasense" / "advisory" / "rules.yml"
        ),
        repository=repository,
    )
