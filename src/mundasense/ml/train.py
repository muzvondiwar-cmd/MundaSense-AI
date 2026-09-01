from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "mundasense-mpl"))

import matplotlib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    median_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.pipeline import Pipeline

from mundasense.constants import (
    FEATURE_ORDER,
    MODEL_BUNDLE_SCHEMA_VERSION,
    MODEL_VERSION,
    RULES_VERSION,
)
from mundasense.data.load import load_dataset
from mundasense.data.quality import build_quality_report
from mundasense.ml.features import feature_contract
from mundasense.ml.preprocessing import build_preprocessor
from mundasense.ml.registry import save_bundle

matplotlib.use("Agg")
from matplotlib import pyplot as plt


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metrics(y_true: pd.Series, predictions: np.ndarray) -> dict[str, float]:
    errors = np.abs(np.asarray(y_true) - predictions)
    return {
        "mae_t_ha": float(mean_absolute_error(y_true, predictions)),
        "rmse_t_ha": float(root_mean_squared_error(y_true, predictions)),
        "r2": float(r2_score(y_true, predictions)),
        "median_absolute_error_t_ha": float(median_absolute_error(y_true, predictions)),
        "absolute_error_p90_t_ha": float(np.quantile(errors, 0.9)),
        "sample_count": len(y_true),
    }


def _training_ranges(frame: pd.DataFrame) -> dict[str, dict[str, float]]:
    ranges: dict[str, dict[str, float]] = {}
    for feature in FEATURE_ORDER:
        series = frame[feature].astype(float)
        ranges[feature] = {
            "min": float(series.min()),
            "q01": float(series.quantile(0.01)),
            "q99": float(series.quantile(0.99)),
            "max": float(series.max()),
            "median": float(series.median()),
        }
    return ranges


def _candidate_estimators(seed: int) -> dict[str, Any]:
    return {
        "naive_median": DummyRegressor(strategy="median"),
        "ridge": Ridge(alpha=2.0),
        "random_forest": RandomForestRegressor(
            n_estimators=180,
            max_depth=10,
            min_samples_leaf=4,
            max_features=0.9,
            random_state=seed,
            n_jobs=1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=160,
            learning_rate=0.04,
            max_depth=2,
            min_samples_leaf=5,
            loss="huber",
            random_state=seed,
        ),
    }


def _save_figures(
    y_true: pd.Series, predictions: np.ndarray, figures_dir: Path, data_label: str
) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    minimum = float(min(y_true.min(), predictions.min()))
    maximum = float(max(y_true.max(), predictions.max()))
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.scatter(y_true, predictions, alpha=0.65, color="#00796B", edgecolor="white", linewidth=0.4)
    ax.plot([minimum, maximum], [minimum, maximum], linestyle="--", color="#D99A00")
    ax.set_xlabel("Actual yield (t/ha)")
    ax.set_ylabel("Predicted yield (t/ha)")
    ax.set_title(f"Actual vs predicted yield - {data_label}")
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(figures_dir / "actual_vs_predicted.png", dpi=160)
    plt.close(fig)

    residuals = np.asarray(y_true) - predictions
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.scatter(
        predictions, residuals, alpha=0.65, color="#1B5E20", edgecolor="white", linewidth=0.4
    )
    ax.axhline(0, linestyle="--", color="#D99A00")
    ax.set_xlabel("Predicted yield (t/ha)")
    ax.set_ylabel("Residual: actual - predicted (t/ha)")
    ax.set_title(f"Residuals - {data_label}")
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(figures_dir / "residuals.png", dpi=160)
    plt.close(fig)


def train_model(
    data_path: Path,
    model_path: Path,
    metrics_dir: Path,
    figures_dir: Path,
    *,
    seed: int = 42,
    minimum_baseline_improvement: float = 0.05,
) -> dict[str, Any]:
    frame = load_dataset(data_path)
    quality = build_quality_report(frame)
    locations = sorted(frame["district"].astype(str).unique())
    if len(locations) < 4:
        raise ValueError("Grouped demonstration split requires at least four districts.")
    calibration_locations = locations[-3:-2]
    test_locations = locations[-2:]
    train_locations = locations[:-3]
    train_frame = frame[frame["district"].isin(train_locations)].copy()
    calibration_frame = frame[frame["district"].isin(calibration_locations)].copy()
    test_frame = frame[frame["district"].isin(test_locations)].copy()

    X_train = train_frame[list(FEATURE_ORDER)]
    y_train = train_frame["yield_t_ha"]
    X_cal = calibration_frame[list(FEATURE_ORDER)]
    y_cal = calibration_frame["yield_t_ha"]
    X_test = test_frame[list(FEATURE_ORDER)]
    y_test = test_frame["yield_t_ha"]

    comparison: list[dict[str, Any]] = []
    fitted: dict[str, Pipeline] = {}
    for name, estimator in _candidate_estimators(seed).items():
        pipeline = Pipeline(
            [("preprocessor", build_preprocessor(scale=True)), ("estimator", estimator)]
        )
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_cal)
        fitted[name] = pipeline
        comparison.append({"model": name, **_metrics(y_cal, predictions)})

    baseline = next(item for item in comparison if item["model"] == "naive_median")
    candidates = [item for item in comparison if item["model"] != "naive_median"]
    champion_record = min(candidates, key=lambda item: (item["mae_t_ha"], item["model"]))
    improvement = (baseline["mae_t_ha"] - champion_record["mae_t_ha"]) / baseline["mae_t_ha"]
    if improvement < minimum_baseline_improvement:
        raise ValueError(
            f"Champion improves validation MAE by {improvement:.1%}; "
            f"minimum release gate is {minimum_baseline_improvement:.1%}."
        )

    champion = fitted[champion_record["model"]]
    calibration_predictions = champion.predict(X_cal)
    calibration_errors = np.abs(y_cal.to_numpy() - calibration_predictions)
    interval_quantile = float(np.quantile(calibration_errors, 0.9, method="higher"))
    test_predictions = champion.predict(X_test)
    test_metrics = _metrics(y_test, test_predictions)
    lower = np.maximum(0.0, test_predictions - interval_quantile)
    upper = test_predictions + interval_quantile
    coverage = float(np.mean((y_test.to_numpy() >= lower) & (y_test.to_numpy() <= upper)))
    test_metrics.update(
        {
            "interval_nominal_coverage": 0.9,
            "interval_empirical_coverage": coverage,
            "mean_interval_width_t_ha": float(np.mean(upper - lower)),
            "baseline_validation_mae_t_ha": baseline["mae_t_ha"],
            "champion_validation_mae_t_ha": champion_record["mae_t_ha"],
            "validation_mae_improvement_over_baseline": float(improvement),
        }
    )
    subgroup_metrics = []
    for district in test_locations:
        mask = test_frame["district"].eq(district).to_numpy()
        subgroup_metrics.append(
            {"district": district, **_metrics(y_test[mask], test_predictions[mask])}
        )

    created_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    package_versions = {
        name: version(name) for name in ("numpy", "pandas", "scikit-learn", "joblib", "matplotlib")
    }
    bundle = {
        "bundle_schema_version": MODEL_BUNDLE_SCHEMA_VERSION,
        "pipeline": champion,
        "feature_spec": feature_contract(),
        "training_ranges": _training_ranges(train_frame),
        "residual_calibration": {
            "method": "held-out grouped absolute residual quantile",
            "nominal_coverage": 0.9,
            "absolute_error_quantile": interval_quantile,
            "calibration_sample_count": len(calibration_frame),
            "calibration_locations": calibration_locations,
        },
        "metrics": {**test_metrics, "subgroups": subgroup_metrics},
        "candidate_comparison": comparison,
        "model_version": MODEL_VERSION,
        "dataset_fingerprint": _fingerprint(data_path),
        "created_at": created_at,
        "is_synthetic": bool(quality["is_synthetic"]),
        "explanation_method": "deterministic one-feature-at-a-time median reference",
        "split_strategy": {
            "type": "held-out district groups",
            "train_locations": train_locations,
            "calibration_locations": calibration_locations,
            "test_locations": test_locations,
            "rationale": "Approximates deployment to locations unseen during model fitting.",
        },
        "package_versions": package_versions,
        "training_config": {
            "seed": seed,
            "features": list(FEATURE_ORDER),
            "target": "yield_t_ha",
            "champion": champion_record["model"],
            "minimum_baseline_improvement": minimum_baseline_improvement,
            "rules_compatibility_version": RULES_VERSION,
        },
    }
    save_bundle(bundle, model_path)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    (metrics_dir / "evaluation.json").write_text(
        json.dumps(
            {
                "model_version": MODEL_VERSION,
                "created_at": created_at,
                "data_quality": quality,
                "split_strategy": bundle["split_strategy"],
                "candidate_comparison": comparison,
                "held_out_test_metrics": test_metrics,
                "subgroup_metrics": subgroup_metrics,
                "training_ranges": bundle["training_ranges"],
                "dataset_fingerprint": bundle["dataset_fingerprint"],
                "is_synthetic": bundle["is_synthetic"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _save_figures(y_test, test_predictions, figures_dir, "synthetic demonstration data")
    return bundle
