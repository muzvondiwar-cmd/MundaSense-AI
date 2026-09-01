from __future__ import annotations

import json
import string
from pathlib import Path
from typing import Any


class TranslationError(ValueError):
    pass


class Translator:
    def __init__(self, locales_dir: Path):
        self.locales_dir = locales_dir
        self.catalogues = {locale: self._load(locale) for locale in ("en", "sn")}
        self.validate_placeholder_parity()

    def _load(self, locale: str) -> dict[str, str]:
        path = self.locales_dir / f"{locale}.json"
        if not path.exists():
            raise TranslationError(f"Translation catalogue missing: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in payload.items()
        ):
            raise TranslationError(f"Translation catalogue must be a string map: {path}")
        return payload

    @staticmethod
    def placeholders(value: str) -> set[str]:
        return {field_name for _, field_name, _, _ in string.Formatter().parse(value) if field_name}

    def validate_placeholder_parity(self) -> None:
        english = self.catalogues["en"]
        shona = self.catalogues["sn"]
        mismatches = []
        for key in english.keys() & shona.keys():
            if self.placeholders(english[key]) != self.placeholders(shona[key]):
                mismatches.append(key)
        if mismatches:
            raise TranslationError(
                f"Placeholder mismatch in translation keys: {', '.join(sorted(mismatches))}"
            )

    def t(self, key: str, locale: str = "en", **values: Any) -> str:
        catalogue = self.catalogues.get(locale, self.catalogues["en"])
        template = catalogue.get(key, self.catalogues["en"].get(key, key))
        try:
            return template.format(**values)
        except KeyError as exc:
            raise TranslationError(f"Missing interpolation value for '{key}': {exc}") from exc

    def missing_shona_keys(self) -> list[str]:
        return sorted(set(self.catalogues["en"]) - set(self.catalogues["sn"]))
