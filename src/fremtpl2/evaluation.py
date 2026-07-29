"""Model calibration and deviance metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_gamma_deviance, mean_poisson_deviance


def frequency_metrics(observed: pd.Series, predicted: pd.Series, exposure: pd.Series) -> dict:
    expected_counts = np.clip(predicted * exposure, 1e-9, None)
    return {
        "poisson_deviance": float(mean_poisson_deviance(observed, expected_counts)),
        "mae_claim_count": float(mean_absolute_error(observed, expected_counts)),
        "observed_frequency": float(observed.sum() / exposure.sum()),
        "predicted_frequency": float(expected_counts.sum() / exposure.sum()),
    }


def severity_metrics(observed: pd.Series, predicted: pd.Series) -> dict:
    return {
        "gamma_deviance": float(mean_gamma_deviance(observed.clip(lower=1e-9), np.clip(predicted, 1e-9, None))),
        "mae": float(mean_absolute_error(observed, predicted)),
        "observed_mean": float(observed.mean()),
        "predicted_mean": float(predicted.mean()),
    }


def calibration_table(
    observed: pd.Series, predicted: pd.Series, weights: pd.Series | None = None, bins: int = 10
) -> pd.DataFrame:
    result = pd.DataFrame({"observed": observed, "predicted": predicted})
    result["weight"] = 1.0 if weights is None else weights
    result["decile"] = pd.qcut(result["predicted"].rank(method="first"), bins, labels=False, duplicates="drop") + 1
    grouped = result.groupby("decile", as_index=False)
    return grouped.apply(
        lambda group: pd.Series(
            {
                "observed": np.average(group["observed"], weights=group["weight"]),
                "predicted": np.average(group["predicted"], weights=group["weight"]),
                "records": len(group),
            }
        ),
        include_groups=False,
    ).reset_index(drop=True)
