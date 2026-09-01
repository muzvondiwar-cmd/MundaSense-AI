from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from mundasense.constants import DEFAULT_LOCALE


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path_from_env(name: str, default: str) -> Path:
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else project_root() / value


def _bool_from_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class AppConfig:
    data_path: Path
    model_path: Path
    database_path: Path
    default_locale: str
    random_seed: int
    log_level: str
    demo_banner: bool
    extension_contact: str

    @classmethod
    def from_env(cls) -> AppConfig:
        locale = os.getenv("MUNDASENSE_DEFAULT_LOCALE", DEFAULT_LOCALE).strip().lower()
        if locale not in {"en", "sn"}:
            raise ValueError("MUNDASENSE_DEFAULT_LOCALE must be 'en' or 'sn'.")
        return cls(
            data_path=_path_from_env("MUNDASENSE_DATA_PATH", "data/sample/maize_demo.csv"),
            model_path=_path_from_env("MUNDASENSE_MODEL_PATH", "models/mundasense_demo_v1.joblib"),
            database_path=_path_from_env(
                "MUNDASENSE_DATABASE_PATH", "data/local/mundasense.sqlite3"
            ),
            default_locale=locale,
            random_seed=int(os.getenv("MUNDASENSE_RANDOM_SEED", "42")),
            log_level=os.getenv("MUNDASENSE_LOG_LEVEL", "INFO").upper(),
            demo_banner=_bool_from_env("MUNDASENSE_DEMO_BANNER", True),
            extension_contact=os.getenv(
                "MUNDASENSE_EXTENSION_CONTACT",
                "Contact your local agricultural extension office.",
            ).strip(),
        )

    @property
    def trusted_models_dir(self) -> Path:
        return project_root() / "models"

    @property
    def rules_path(self) -> Path:
        return Path(__file__).parent / "advisory" / "rules.yml"

    @property
    def locales_dir(self) -> Path:
        return Path(__file__).parent / "i18n"
