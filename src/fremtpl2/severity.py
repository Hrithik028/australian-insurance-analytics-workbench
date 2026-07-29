"""Interpretable Gamma severity GLM."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from src.config import Settings, settings
from src.fremtpl2.evaluation import calibration_table, severity_metrics
from src.fremtpl2.preprocessing import engineer, split_train_validation_test

FORMULA = (
    "ClaimAmount ~ C(Area) + VehPower + C(VehAgeBand) + C(DrivAgeBand) + "
    "C(BonusMalusBand) + C(VehBrand) + C(VehGas) + LogDensity + C(Region)"
)


def train_severity_model(config: Settings = settings) -> dict[str, object]:
    frame = pd.read_parquet(config.french_processed / "fremtpl2_severity_features.parquet")
    frame = engineer(frame.loc[frame["ClaimAmount"].gt(0)].copy())
    train, validation, test = split_train_validation_test(frame)
    model = smf.glm(
        formula=FORMULA,
        data=train,
        family=sm.families.Gamma(link=sm.families.links.Log()),
    ).fit(maxiter=100)
    predicted = np.asarray(model.predict(test))
    metrics = severity_metrics(test["ClaimAmount"], predicted)
    model_dir = config.root / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model.save(model_dir / "severity_glm.pkl")
    coefficients = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "std_error": model.bse.values,
            "ci_lower": model.conf_int()[0].values,
            "ci_upper": model.conf_int()[1].values,
        }
    )
    coefficients.to_parquet(config.french_processed / "severity_coefficients.parquet", index=False)
    calibration_table(test["ClaimAmount"], pd.Series(predicted, index=test.index)).to_parquet(
        config.french_processed / "severity_calibration.parquet", index=False
    )
    predictions = test[["IDpol", "ClaimAmount"]].copy()
    predictions["predicted_severity"] = predicted
    predictions["residual"] = predictions["ClaimAmount"] - predicted
    predictions.to_parquet(config.french_processed / "severity_predictions.parquet", index=False)
    large_loss_threshold = float(train["ClaimAmount"].quantile(0.99))
    summary = {
        "trained_at": datetime.now(UTC).isoformat(),
        "model": "Gamma GLM with log link",
        "formula": FORMULA,
        "target_rule": "positive ClaimAmount only; no capping or winsorisation",
        "policy_id_excluded": True,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "test_rows": len(test),
        "large_loss_p99": large_loss_threshold,
        **metrics,
    }
    (config.french_processed / "severity_model_metrics.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def predict_severity(frame: pd.DataFrame, config: Settings = settings) -> np.ndarray:
    model = sm.load(config.root / "models/severity_glm.pkl")
    return np.asarray(model.predict(engineer(frame)))
