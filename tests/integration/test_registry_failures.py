from __future__ import annotations

from pathlib import Path

import pytest

from mundasense.ml.registry import load_bundle
from mundasense.schemas import ModelBundleError


def test_missing_bundle_is_controlled(tmp_path: Path) -> None:
    with pytest.raises(ModelBundleError, match=r"Run: python scripts/train_model\.py"):
        load_bundle(tmp_path / "missing.joblib", trusted_directory=tmp_path)


def test_corrupt_bundle_checksum_is_controlled(tmp_path: Path) -> None:
    path = tmp_path / "corrupt.joblib"
    path.write_bytes(b"not a model")
    path.with_suffix(".joblib.sha256").write_text("0" * 64, encoding="ascii")
    with pytest.raises(ModelBundleError, match="checksum mismatch"):
        load_bundle(path, trusted_directory=tmp_path)
