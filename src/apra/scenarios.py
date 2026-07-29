"""Transparent claims-cost-index pricing scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Scenario:
    severity_trend: float = 0.05
    frequency_trend: float = 0.02
    inflation: float = 0.03
    expense_change: float = 0.00
    risk_margin: float = 0.02
    target_margin: float = 0.05
    credibility: float = 1.0
    management_adjustment: float = 0.0


def calculate_scenario(inputs: Scenario, baseline_index: float = 100.0) -> dict[str, float]:
    stressed_claims = baseline_index * (1 + inputs.severity_trend) * (1 + inputs.frequency_trend)
    inflated_claims = stressed_claims * (1 + inputs.inflation)
    technical = inflated_claims * (1 + inputs.expense_change + inputs.risk_margin)
    margin_indication = technical / (1 - inputs.target_margin)
    credible = baseline_index + inputs.credibility * (margin_indication - baseline_index)
    recommendation = credible * (1 + inputs.management_adjustment)
    return {
        **asdict(inputs),
        "baseline_index": baseline_index,
        "stressed_claims_cost": stressed_claims,
        "inflated_claims_cost": inflated_claims,
        "technical_indication": technical,
        "credibility_weighted_indication": credible,
        "simulated_recommendation": recommendation,
        "simulated_rate_change": recommendation / baseline_index - 1,
    }
