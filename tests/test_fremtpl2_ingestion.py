import pandas as pd
import pytest

from src.fremtpl2.validation import validate_frequency, validate_severity


def _frequency():
    return pd.DataFrame(
        {
            "IDpol": [1],
            "ClaimNb": [0],
            "Exposure": [1.0],
            "Area": ["A"],
            "VehPower": [5],
            "VehAge": [2],
            "DrivAge": [30],
            "BonusMalus": [50],
            "VehBrand": ["B1"],
            "VehGas": ["Regular"],
            "Density": [100],
            "Region": ["R1"],
        }
    )


def test_frequency_schema_and_exposure():
    validate_frequency(_frequency())
    invalid = _frequency()
    invalid.loc[0, "Exposure"] = 0
    with pytest.raises(ValueError, match="strictly positive"):
        validate_frequency(invalid)


def test_severity_schema_and_positive_filter_rule():
    severity = pd.DataFrame({"IDpol": [1, 1], "ClaimAmount": [100.0, -1.0]})
    validate_severity(severity)
    assert severity.loc[severity["ClaimAmount"].gt(0), "ClaimAmount"].tolist() == [100.0]
