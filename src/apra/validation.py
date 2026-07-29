"""Row-level APRA quality flags."""

from __future__ import annotations

import pandas as pd

from src.apra.schema import CATEGORY_COLUMNS, KNOWN_STATES


def add_quality_flags(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    false = pd.Series(False, index=result.index)

    def missing(column: str) -> pd.Series:
        return result[column].isna() if column in result else false

    def negative(column: str) -> pd.Series:
        return result[column].lt(0).fillna(False) if column in result else false

    result["is_negative_payment"] = negative("gross_claim_payments")
    result["is_negative_incurred"] = negative("gross_claims_incurred")
    result["is_negative_earned_premium"] = negative("gross_earned_premium")
    result["is_missing_claim_count"] = missing("number_of_claims_reported1")
    result["is_missing_policy_count"] = missing("number_of_risks_written1")
    result["is_missing_exposure"] = missing("risk_in_force_weighted")
    result["is_missing_premium"] = missing("gross_earned_premium")
    result["is_finalised_gt_reported"] = false
    if {"number_of_claims_finalised", "number_of_claims_reported1"} <= set(result):
        result["is_finalised_gt_reported"] = (
            result["number_of_claims_finalised"].notna()
            & result["number_of_claims_reported1"].notna()
            & result["number_of_claims_finalised"].gt(result["number_of_claims_reported1"])
        )
    year_columns = [name for name in result if name.endswith("_year")]
    result["is_invalid_year"] = false
    for column in year_columns:
        result["is_invalid_year"] |= result[column].notna() & ~result[column].between(1900, 2026)
    result["is_year_sequence_anomaly"] = false
    if {"accident_year", "reported_year"} <= set(result):
        result["is_year_sequence_anomaly"] |= (
            result["reported_year"].notna()
            & result["accident_year"].notna()
            & result["reported_year"].lt(result["accident_year"])
        )
    if {"reported_year", "finalised_year"} <= set(result):
        result["is_year_sequence_anomaly"] |= (
            result["finalised_year"].notna()
            & result["reported_year"].notna()
            & result["finalised_year"].lt(result["reported_year"])
        )
    result["is_unknown_category"] = false
    if "state_jurisdiction" in result:
        result["is_unknown_category"] = ~result["state_jurisdiction"].isin(KNOWN_STATES)
    for column in set(CATEGORY_COLUMNS) & set(result.columns):
        result["is_unknown_category"] |= (
            result[column].astype("string").str.strip().str.lower().eq("unknown").fillna(False)
        )
    business_keys = [
        column
        for column in result.columns
        if column
        not in {
            "source_file",
            "source_sheet",
            "source_report_type",
            "source_dimension",
            "ingested_at",
        }
        and not column.startswith("is_")
    ]
    result["is_potential_duplicate"] = result.duplicated(business_keys, keep=False)
    result["is_schema_exception"] = result["reporting_year"].isna()
    return result


def exception_rows(frame: pd.DataFrame) -> pd.DataFrame:
    flags = [column for column in frame if column.startswith("is_")]
    return frame.loc[frame[flags].any(axis=1)].copy()
