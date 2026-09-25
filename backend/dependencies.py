from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.config import AppConfig
from mundasense.i18n.translator import Translator
from mundasense.ml.registry import load_bundle
from mundasense.services.assessment_service import AssessmentService
from mundasense.storage.assessment_repository import AssessmentRepository
from mundasense.storage.database import Database


@dataclass(slots=True)
class Runtime:
    config: AppConfig
    translator: Translator
    bundle: dict[str, Any]
    repository: AssessmentRepository
    engine: AdvisoryEngine
    service: AssessmentService


@lru_cache(maxsize=1)
def get_runtime() -> Runtime:
    """Load trusted local assets once per API process."""
    config = AppConfig.from_env()
    translator = Translator(config.locales_dir)
    bundle = load_bundle(config.model_path, trusted_directory=config.trusted_models_dir)
    repository = AssessmentRepository(Database(config.database_path))
    engine = AdvisoryEngine(config.rules_path)
    service = AssessmentService(bundle=bundle, advisory_engine=engine, repository=repository)
    return Runtime(
        config=config,
        translator=translator,
        bundle=bundle,
        repository=repository,
        engine=engine,
        service=service,
    )
