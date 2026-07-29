import pytest

from src.fremtpl2.premium import Loadings, calculate_loaded_premium


def test_loading_calculation():
    result = calculate_loaded_premium(
        100,
        Loadings(
            expense=0.1,
            commission=0,
            risk_margin=0,
            profit_margin=0,
            tax_or_levy=0.1,
            reinsurance=0,
            management_adjustment=0,
        ),
    )
    assert result["simulated_indicated_premium"] == pytest.approx(121)
