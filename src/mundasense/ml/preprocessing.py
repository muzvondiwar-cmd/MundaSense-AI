from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mundasense.constants import FEATURE_ORDER


def build_preprocessor(*, scale: bool = True) -> ColumnTransformer:
    steps: list[tuple[str, object]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scaler", StandardScaler()))
    numeric = Pipeline(steps)
    return ColumnTransformer(
        [("numeric", numeric, list(FEATURE_ORDER))],
        remainder="drop",
        verbose_feature_names_out=False,
    )
