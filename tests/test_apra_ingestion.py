import pandas as pd

from src.apra.cleaning import standardise_frame


def test_column_standardisation_and_numeric_conversion():
    source = pd.DataFrame({"Gross claim Payments ($)": ["10", "-4"], "A B": [1, 2]})
    result, mapping = standardise_frame(source)
    assert list(result.columns) == ["gross_claim_payments", "a_b"]
    assert result["gross_claim_payments"].tolist() == [10, -4]
    assert mapping["gross_claim_payments"] == "Gross claim Payments ($)"


def test_negative_values_are_preserved():
    result, _ = standardise_frame(pd.DataFrame({"Gross claims Incurred ($)": ["-25"]}))
    assert result.loc[0, "gross_claims_incurred"] == -25
