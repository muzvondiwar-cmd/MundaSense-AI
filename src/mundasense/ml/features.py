from __future__ import annotations

from typing import Any

import pandas as pd

from mundasense.constants import FEATURE_ORDER, FEATURE_SPEC


def feature_contract() -> list[dict[str, Any]]:
    return [{"name": name, **FEATURE_SPEC[name]} for name in FEATURE_ORDER]


def enforce_feature_order(values: dict[str, float]) -> pd.DataFrame:
    missing = [name for name in FEATURE_ORDER if name not in values]
    unexpected = sorted(set(values) - set(FEATURE_ORDER))
    if missing or unexpected:
        messages = []
        if missing:
            messages.append(f"missing features: {', '.join(missing)}")
        if unexpected:
            messages.append(f"unexpected features: {', '.join(unexpected)}")
        raise ValueError("; ".join(messages))
    return pd.DataFrame([[float(values[name]) for name in FEATURE_ORDER]], columns=FEATURE_ORDER)
