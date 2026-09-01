from __future__ import annotations

from pathlib import Path
from typing import Any

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.config import AppConfig
from mundasense.i18n.translator import Translator
from mundasense.ml.registry import load_bundle
from mundasense.storage.database import Database


def readiness(config: AppConfig) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    try:
        bundle = load_bundle(config.model_path, trusted_directory=config.trusted_models_dir)
        checks["model"] = {"ok": True, "detail": bundle["model_version"]}
    except Exception as exc:  # noqa: BLE001 - readiness must aggregate controlled failures
        checks["model"] = {"ok": False, "detail": str(exc)}
    try:
        engine = AdvisoryEngine(config.rules_path)
        checks["rules"] = {"ok": True, "detail": engine.catalogue["catalogue_version"]}
    except Exception as exc:  # noqa: BLE001
        checks["rules"] = {"ok": False, "detail": str(exc)}
    try:
        translator = Translator(config.locales_dir)
        checks["locales"] = {
            "ok": True,
            "detail": f"English + Shona ({len(translator.missing_shona_keys())} fallback keys)",
        }
    except Exception as exc:  # noqa: BLE001
        checks["locales"] = {"ok": False, "detail": str(exc)}
    ok, detail = Database(config.database_path).readiness()
    checks["database"] = {"ok": ok, "detail": detail}
    required_dirs = [Path("data"), Path("models"), Path("reports"), Path("docs")]
    missing_dirs = [str(path) for path in required_dirs if not path.exists()]
    checks["directories"] = {
        "ok": not missing_dirs,
        "detail": "present" if not missing_dirs else f"missing: {', '.join(missing_dirs)}",
    }
    return {"ready": all(item["ok"] for item in checks.values()), "checks": checks}
