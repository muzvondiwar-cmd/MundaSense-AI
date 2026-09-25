from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.config import AppConfig
from mundasense.i18n.translator import Translator
from mundasense.logging_config import configure_logging
from mundasense.ml.registry import load_bundle
from mundasense.services.assessment_service import AssessmentService
from mundasense.storage.assessment_repository import AssessmentRepository
from mundasense.storage.catalog_repository import CatalogRepository
from mundasense.storage.database import Database


@dataclass(slots=True)
class Runtime:
    config: AppConfig
    translator: Translator
    bundle: dict[str, Any]
    repository: AssessmentRepository
    engine: AdvisoryEngine
    service: AssessmentService
    catalog: CatalogRepository | None = None


@lru_cache(maxsize=1)
def get_runtime() -> Runtime:
    """Load trusted local assets once per API process."""
    config = AppConfig.from_env()
    configure_logging(config.log_level)
    translator = Translator(config.locales_dir)
    bundle = load_bundle(config.model_path, trusted_directory=config.trusted_models_dir)
    database_target = os.getenv("MUNDASENSE_DATABASE_URL") or config.database_path
    repository = AssessmentRepository(Database(database_target))
    engine = AdvisoryEngine(config.rules_path)
    service = AssessmentService(bundle=bundle, advisory_engine=engine, repository=repository)
    catalog = CatalogRepository(repository.database)
    return Runtime(
        config=config,
        translator=translator,
        bundle=bundle,
        repository=repository,
        engine=engine,
        service=service,
        catalog=catalog,
    )
