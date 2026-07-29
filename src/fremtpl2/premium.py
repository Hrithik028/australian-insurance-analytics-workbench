"""Pure-premium estimate and transparent loading simulator."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from src.fremtpl2.frequency import predict_frequency
from src.fremtpl2.severity import predict_severity


@dataclass(frozen=True)
class Loadings:
    expense: float = 0.15
    commission: float = 0.10
    risk_margin: float = 0.05
    profit_margin: float = 0.05
    tax_or_levy: float = 0.10
    reinsurance: float = 0.03
    management_adjustment: float = 0.0


def calculate_loaded_premium(claims_cost: float, loadings: Loadings) -> dict[str, float]:
    subtotal = claims_cost * (1 + loadings.expense + loadings.commission + loadings.risk_margin + loadings.reinsurance)
    before_tax = subtotal / (1 - loadings.profit_margin)
    after_tax = before_tax * (1 + loadings.tax_or_levy)
    indicated = after_tax * (1 + loadings.management_adjustment)
    return {
        **asdict(loadings),
        "technical_claims_cost": claims_cost,
        "subtotal_after_cost_loadings": subtotal,
        "premium_before_tax": before_tax,
        "simulated_indicated_premium": indicated,
    }


def estimate_technical_claims_cost(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["estimated_frequency"] = predict_frequency(frame)
    result["estimated_severity"] = predict_severity(frame)
    result["estimated_technical_claims_cost"] = result["estimated_frequency"] * result["estimated_severity"]
    return result
