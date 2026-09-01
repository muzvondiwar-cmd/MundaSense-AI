from __future__ import annotations

import altair as alt
import pandas as pd

from mundasense.i18n.translator import Translator
from mundasense.schemas import AssessmentResult


def interval_chart(result: AssessmentResult) -> alt.Chart:
    frame = pd.DataFrame(
        {
            "label": ["Plausible range"],
            "lower": [result.interval_lower_t_ha],
            "upper": [result.interval_upper_t_ha],
            "prediction": [result.predicted_yield_t_ha],
        }
    )
    range_line = (
        alt.Chart(frame)
        .mark_rule(strokeWidth=8, color="#B9D8BD")
        .encode(
            x=alt.X("lower:Q", title="Yield (t/ha)"), x2="upper:Q", y=alt.Y("label:N", title=None)
        )
    )
    point = (
        alt.Chart(frame)
        .mark_point(size=180, filled=True, color="#1B5E20")
        .encode(x="prediction:Q", y="label:N", tooltip=["prediction", "lower", "upper"])
    )
    return (range_line + point).properties(height=80)


def driver_chart(result: AssessmentResult, translator: Translator, locale: str) -> alt.Chart:
    frame = pd.DataFrame(
        [
            {
                "feature": translator.t(driver.display_key, locale),
                "contribution": driver.contribution,
                "direction": driver.direction,
            }
            for driver in result.top_drivers
        ]
    )
    return (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("contribution:Q", title="Approximate contribution to estimate (t/ha)"),
            y=alt.Y("feature:N", sort="-x", title=None),
            color=alt.Color(
                "direction:N",
                scale=alt.Scale(
                    domain=["increased", "decreased", "neutral"],
                    range=["#2E7D32", "#D99A00", "#8A9A8C"],
                ),
                legend=None,
            ),
            tooltip=["feature", "contribution", "direction"],
        )
        .properties(height=170)
    )
