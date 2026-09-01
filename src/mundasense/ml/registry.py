from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import joblib

from mundasense.constants import MODEL_BUNDLE_SCHEMA_VERSION
from mundasense.schemas import ModelBundleError

REQUIRED_BUNDLE_KEYS = {
    "bundle_schema_version",
    "pipeline",
    "feature_spec",
    "training_ranges",
    "residual_calibration",
    "metrics",
    "candidate_comparison",
    "model_version",
    "dataset_fingerprint",
    "created_at",
    "is_synthetic",
    "explanation_method",
    "split_strategy",
    "package_versions",
    "training_config",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_bundle(bundle: Any) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ModelBundleError("Model bundle is not a mapping.")
    missing = sorted(REQUIRED_BUNDLE_KEYS - set(bundle))
    if missing:
        raise ModelBundleError(f"Model bundle missing keys: {', '.join(missing)}")
    if bundle["bundle_schema_version"] != MODEL_BUNDLE_SCHEMA_VERSION:
        raise ModelBundleError(
            f"Unsupported model bundle schema: {bundle['bundle_schema_version']}"
        )
    pipeline = bundle["pipeline"]
    if not hasattr(pipeline, "predict"):
        raise ModelBundleError("Model bundle pipeline does not support prediction.")
    if not bundle["residual_calibration"].get("absolute_error_quantile"):
        raise ModelBundleError("Model bundle is missing residual calibration.")
    return bundle


def save_bundle(bundle: dict[str, Any], path: Path) -> tuple[Path, Path]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    joblib.dump(validate_bundle(bundle), temporary, compress=3)
    temporary.replace(path)
    checksum_path = path.with_suffix(path.suffix + ".sha256")
    checksum_path.write_text(f"{sha256_file(path)}  {path.name}\n", encoding="ascii")
    return path, checksum_path


def load_bundle(path: Path, *, trusted_directory: Path) -> dict[str, Any]:
    resolved_path = path.resolve()
    resolved_trusted = trusted_directory.resolve()
    if not resolved_path.is_relative_to(resolved_trusted):
        raise ModelBundleError(
            "Refusing to load a serialised model outside the configured trusted models directory."
        )
    if not resolved_path.exists():
        raise ModelBundleError(
            f"Model bundle not found: {resolved_path}. Run: python scripts/train_model.py"
        )
    checksum_path = resolved_path.with_suffix(resolved_path.suffix + ".sha256")
    if not checksum_path.exists():
        raise ModelBundleError(
            "Model checksum sidecar is missing; retrain or restore the trusted release."
        )
    expected = checksum_path.read_text(encoding="ascii").split()[0]
    actual = sha256_file(resolved_path)
    if actual != expected:
        raise ModelBundleError("Model checksum mismatch; the bundle may be corrupted or tampered.")
    try:
        bundle = joblib.load(resolved_path)
    except Exception as exc:
        raise ModelBundleError(f"Could not load the trusted model bundle: {exc}") from exc
    return validate_bundle(bundle)
