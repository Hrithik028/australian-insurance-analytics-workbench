from src.fremtpl2.severity import FORMULA


def test_policy_identifier_excluded_from_severity_formula():
    assert "IDpol" not in FORMULA
