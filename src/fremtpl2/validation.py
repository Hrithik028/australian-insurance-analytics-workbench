"""freMTPL2 schema and value contracts."""

from __future__ import annotations

import pandas as pd

FREQUENCY_COLUMNS = {
    "IDpol",
    "ClaimNb",
    "Exposure",
    "Area",
    "VehPower",
    "VehAge",
    "DrivAge",
    "BonusMalus",
    "VehBrand",
    "VehGas",
    "Density",
    "Region",
}
SEVERITY_COLUMNS = {"IDpol", "ClaimAmount"}


def validate_schema(frame: pd.DataFrame, expected: set[str], label: str) -> None:
    missing = expected - set(frame.columns)
    if missing:
        raise ValueError(f"{label} schema changed; missing columns: {sorted(missing)}")


def validate_frequency(frame: pd.DataFrame) -> None:
    validate_schema(frame, FREQUENCY_COLUMNS, "Frequency")
    if frame["IDpol"].duplicated().any():
        raise ValueError("Frequency policy identifiers must be unique")
    if frame["Exposure"].isna().any() or frame["Exposure"].le(0).any():
        raise ValueError("Exposure must be complete and strictly positive")
    if frame["ClaimNb"].isna().any() or frame["ClaimNb"].lt(0).any():
        raise ValueError("Claim counts must be complete and non-negative")


def validate_severity(frame: pd.DataFrame) -> None:
    validate_schema(frame, SEVERITY_COLUMNS, "Severity")
    if frame["IDpol"].isna().any():
        raise ValueError("Severity policy identifiers must be complete")
