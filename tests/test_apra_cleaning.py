from src.apra.validation import add_quality_flags


def test_quality_flags_preserve_and_identify_exceptions(claim_frame):
    result = add_quality_flags(claim_frame)
    assert result.loc[1, "gross_claim_payments"] == -25
    assert bool(result.loc[1, "is_negative_payment"])
    assert bool(result.loc[1, "is_negative_incurred"])
    assert bool(result.loc[1, "is_finalised_gt_reported"])
    assert bool(result.loc[1, "is_year_sequence_anomaly"])
    assert bool(result.loc[1, "is_unknown_category"])


def test_invalid_sequence_detected(claim_frame):
    result = add_quality_flags(claim_frame)
    assert bool(result.loc[2, "is_year_sequence_anomaly"])
