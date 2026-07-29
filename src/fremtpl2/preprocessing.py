"""Leakage-aware train/test preparation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

FEATURES = [
    "Area",
    "VehPower",
    "VehAge",
    "DrivAge",
    "BonusMalus",
    "VehBrand",
    "VehGas",
    "Density",
    "Region",
]


def split_policy_ids(
    frame: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_ids, test_ids = train_test_split(
        frame["IDpol"].drop_duplicates(), test_size=test_size, random_state=random_state
    )
    train = frame.loc[frame["IDpol"].isin(train_ids)].copy()
    test = frame.loc[frame["IDpol"].isin(test_ids)].copy()
    if set(train["IDpol"]) & set(test["IDpol"]):
        raise AssertionError("Policy leakage detected")
    return train, test


def split_train_validation_test(
    frame: pd.DataFrame, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_validation, test = split_policy_ids(frame, test_size=0.2, random_state=random_state)
    train, validation = split_policy_ids(train_validation, test_size=0.25, random_state=random_state)
    return train, validation, test


def engineer(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["VehAgeBand"] = pd.cut(result["VehAge"], [-1, 1, 5, 10, 20, float("inf")], labels=False).astype(str)
    result["DrivAgeBand"] = pd.cut(result["DrivAge"], [17, 24, 34, 49, 64, float("inf")], labels=False).astype(str)
    result["BonusMalusBand"] = pd.cut(result["BonusMalus"], [0, 50, 75, 100, 150, float("inf")], labels=False).astype(
        str
    )
    result["LogDensity"] = np.log(result["Density"].clip(lower=1))
    return result
