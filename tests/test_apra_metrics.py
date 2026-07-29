import math

from src.apra.metrics import add_claim_metrics
from src.utils import safe_divide


def test_safe_division():
    assert safe_divide(10, 2) == 5
    assert math.isnan(safe_divide(1, 0))


def test_claim_metrics(claim_frame):
    result = add_claim_metrics(claim_frame)
    assert result.loc[0, "finalisation_ratio"] == 0.5
    assert result.loc[0, "average_incurred_per_reported_claim"] == 20
    assert result.loc[0, "outstanding_incurred_proxy"] == 100
    assert math.isnan(result.loc[1, "finalisation_ratio"])
