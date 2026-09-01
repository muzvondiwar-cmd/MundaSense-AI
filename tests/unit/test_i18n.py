from __future__ import annotations

from mundasense.config import project_root
from mundasense.i18n.translator import Translator


def translator() -> Translator:
    return Translator(project_root() / "src" / "mundasense" / "i18n")


def test_english_catalogue_loads_critical_key() -> None:
    assert translator().t("risk.high", "en") == "High yield risk"


def test_missing_shona_key_falls_back_to_english() -> None:
    instance = translator()
    assert instance.t("risk.explanation.high", "sn") == instance.t("risk.explanation.high", "en")


def test_placeholders_have_parity() -> None:
    instance = translator()
    assert instance.placeholders(instance.catalogues["en"]["warning.unusual"]) == {
        "feature",
        "lower",
        "upper",
    }
