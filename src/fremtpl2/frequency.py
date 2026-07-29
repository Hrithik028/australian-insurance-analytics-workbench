"""Interpretable Poisson and Negative Binomial frequency GLMs."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from src.config import Settings, settings
from src.fremtpl2.evaluation import calibration_table, frequency_metrics
from src.fremtpl2.preprocessing import engineer, split_train_validation_test

FORMULA = (
    "ClaimNb ~ C(Area) + VehPower + C(VehAgeBand) + C(DrivAgeBand) + "
    "C(BonusMalusBand) + C(VehBrand) + C(VehGas) + LogDensity + C(Region)"
)


def _fit(train: pd.DataFrame, family: sm.families.Family):
    return smf.glm(
        formula=FORMULA,
        data=train,
        family=family,
        offset=np.log(train["Exposure"]),
    ).fit(maxiter=100)


def train_frequency_model(config: Settings = settings) -> dict[str, object]:
    path = config.french_processed / "fremtpl2_frequency.parquet"
    frame = engineer(pd.read_parquet(path))
    train, validation, test = split_train_validation_test(frame)
    poisson = _fit(train, sm.families.Poisson())
    dispersion = float(poisson.pearson_chi2 / poisson.df_resid)
    poisson_validation_counts = poisson.predict(validation, offset=np.log(validation["Exposure"]))
    validation_comparison = {
        "Poisson GLM": frequency_metrics(
            validation["ClaimNb"],
            poisson_validation_counts / validation["Exposure"],
            validation["Exposure"],
        )
    }
    selected = poisson
    selected_name = "Poisson GLM"
    challenger = None
    if dispersion > 1.5:
        challenger = _fit(train, sm.families.NegativeBinomial(alpha=max(dispersion - 1, 0.01)))
        challenger_validation_counts = challenger.predict(validation, offset=np.log(validation["Exposure"]))
        validation_comparison["Negative Binomial GLM"] = frequency_metrics(
            validation["ClaimNb"],
            challenger_validation_counts / validation["Exposure"],
            validation["Exposure"],
        )
        selected = challenger
        selected_name = "Negative Binomial GLM"
    expected_counts = selected.predict(test, offset=np.log(test["Exposure"]))
    predicted_frequency = expected_counts / test["Exposure"]
    metrics = frequency_metrics(test["ClaimNb"], predicted_frequency, test["Exposure"])
    metrics["dispersion"] = dispersion
    model_dir = config.root / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    selected.save(model_dir / "frequency_glm.pkl")
    coefficients = pd.DataFrame(
        {
            "term": selected.params.index,
            "coefficient": selected.params.values,
            "std_error": selected.bse.values,
            "ci_lower": selected.conf_int()[0].values,
            "ci_upper": selected.conf_int()[1].values,
        }
    )
    coefficients.to_parquet(config.french_processed / "frequency_coefficients.parquet", index=False)
    calibration = calibration_table(test["ClaimNb"] / test["Exposure"], predicted_frequency, test["Exposure"])
    calibration.to_parquet(config.french_processed / "frequency_calibration.parquet", index=False)
    predictions = test[["IDpol", "ClaimNb", "Exposure"]].copy()
    predictions["predicted_frequency"] = predicted_frequency
    predictions["predicted_claim_count"] = expected_counts
    predictions.to_parquet(config.french_processed / "frequency_predictions.parquet", index=False)
    summary = {
        "trained_at": datetime.now(UTC).isoformat(),
        "model": selected_name,
        "baseline": "Poisson GLM",
        "challenger": "Negative Binomial GLM" if challenger is not None else None,
        "formula": FORMULA,
        "offset": "log(Exposure)",
        "policy_id_excluded": True,
        "validation_comparison": validation_comparison,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "test_rows": len(test),
        **metrics,
    }
    (config.french_processed / "frequency_model_metrics.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def predict_frequency(frame: pd.DataFrame, config: Settings = settings) -> np.ndarray:
    model = sm.load(config.root / "models/frequency_glm.pkl")
    prepared = engineer(frame)
    return np.asarray(model.predict(prepared, offset=np.zeros(len(prepared))))
