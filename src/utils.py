"""Shared helpers."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd


def snake_case(value: object) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"[^0-9A-Za-z]+", "_", text).strip("_").lower()
    text = re.sub(r"_+", "_", text)
    return text or "unnamed"


def unique_names(values: list[object]) -> list[str]:
    counts: dict[str, int] = {}
    result = []
    for value in values:
        base = snake_case(value)
        counts[base] = counts.get(base, 0) + 1
        result.append(base if counts[base] == 1 else f"{base}_{counts[base]}")
    return result


def safe_divide(numerator: object, denominator: object) -> object:
    if isinstance(numerator, pd.Series) or isinstance(denominator, pd.Series):
        num = pd.to_numeric(numerator, errors="coerce")
        den = pd.to_numeric(denominator, errors="coerce")
        return num.div(den).where(den.notna() & den.ne(0))
    try:
        if denominator is None or pd.isna(denominator) or float(denominator) == 0:
            return np.nan
        return float(numerator) / float(denominator)
    except (TypeError, ValueError):
        return np.nan


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
