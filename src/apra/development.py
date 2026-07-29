"""Illustrative APRA development matrices."""

from __future__ import annotations

import pandas as pd


def development_matrix(
    frame: pd.DataFrame,
    value: str = "gross_claims_incurred",
    origin: str = "accident_year",
    valuation: str = "reporting_year",
) -> pd.DataFrame:
    data = frame.dropna(subset=[origin, valuation, value]).copy()
    data["development_period"] = data[valuation] - data[origin]
    data = data.loc[data["development_period"].ge(0)]
    return data.pivot_table(
        index=origin,
        columns="development_period",
        values=value,
        aggfunc="sum",
    ).sort_index()
