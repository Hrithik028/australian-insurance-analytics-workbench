import pytest

from src.apra.scenarios import Scenario, calculate_scenario


def test_scenario_is_transparent_and_reconciles():
    result = calculate_scenario(Scenario(severity_trend=0.1, frequency_trend=0.0))
    assert result["stressed_claims_cost"] == pytest.approx(110)
    assert result["simulated_recommendation"] > result["baseline_index"]
