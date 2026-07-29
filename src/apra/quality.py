"""APRA quality summaries."""

from __future__ import annotations

import pandas as pd


def quality_summary(frame: pd.DataFrame) -> pd.DataFrame:
    flags = [column for column in frame if column.startswith("is_")]
    return pd.DataFrame(
        {
            "check": flags,
            "exception_count": [int(frame[column].sum()) for column in flags],
            "exception_rate": [float(frame[column].mean()) for column in flags],
        }
    )
