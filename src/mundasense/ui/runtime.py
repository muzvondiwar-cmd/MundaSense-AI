from __future__ import annotations

from typing import Any

import streamlit as st

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.config import AppConfig
from mundasense.i18n.translator import Translator
from mundasense.ml.registry import load_bundle
from mundasense.services.assessment_service import AssessmentService
from mundasense.storage.assessment_repository import AssessmentRepository
from mundasense.storage.database import Database


@st.cache_resource
def get_runtime() -> dict[str, Any]:
    config = AppConfig.from_env()
    translator = Translator(config.locales_dir)
    bundle = load_bundle(config.model_path, trusted_directory=config.trusted_models_dir)
    repository = AssessmentRepository(Database(config.database_path))
    engine = AdvisoryEngine(config.rules_path)
    service = AssessmentService(bundle=bundle, advisory_engine=engine, repository=repository)
    return {
        "config": config,
        "translator": translator,
        "bundle": bundle,
        "repository": repository,
        "engine": engine,
        "service": service,
    }
