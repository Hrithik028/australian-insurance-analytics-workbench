"""APRA column and value cleaning without erasing source evidence."""

from __future__ import annotations

import pandas as pd

from src.apra.schema import NUMERIC_COLUMNS, YEAR_COLUMNS
from src.utils import unique_names


def standardise_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    original = [str(value) if value is not None else "" for value in frame.columns]
    cleaned = unique_names(original)
    mapping = dict(zip(cleaned, original, strict=True))
    result = frame.copy()
    result.columns = cleaned
    result = result.loc[:, ~result.columns.str.startswith("unnamed")]
    for column in set(NUMERIC_COLUMNS) & set(result.columns):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    for column in set(YEAR_COLUMNS) & set(result.columns):
        result[column] = pd.to_numeric(result[column], errors="coerce").astype("Int64")
    return result, mapping
