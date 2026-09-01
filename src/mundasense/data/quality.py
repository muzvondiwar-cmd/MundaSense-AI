from __future__ import annotations

from typing import Any

import pandas as pd

from mundasense.constants import FEATURE_ORDER


def build_quality_report(frame: pd.DataFrame) -> dict[str, Any]:
    numeric = [*FEATURE_ORDER, "yield_t_ha"]
    outliers: dict[str, int] = {}
    for column in numeric:
        series = frame[column].dropna()
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers[column] = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
    return {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "duplicate_record_ids": int(frame["record_id"].duplicated().sum()),
        "missing_by_column": {key: int(value) for key, value in frame.isna().sum().items()},
        "iqr_outlier_count": outliers,
        "data_sources": sorted(frame["data_source"].astype(str).unique().tolist()),
        "is_synthetic": bool(frame["is_synthetic"].astype(bool).all()),
        "district_count": int(frame["district"].nunique()),
        "season_count": int(frame["season"].nunique()),
        "status": "pass" if not frame[numeric].isna().all(axis=None) else "fail",
    }

