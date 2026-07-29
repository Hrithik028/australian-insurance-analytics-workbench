"""Supported APRA aggregate metrics."""

from __future__ import annotations

import pandas as pd

from src.utils import safe_divide


def add_claim_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    reported = result.get("number_of_claims_reported1")
    finalised = result.get("number_of_claims_finalised")
    incurred = result.get("gross_claims_incurred")
    paid = result.get("gross_claim_payments")
    if reported is not None and finalised is not None:
        result["outstanding_claim_count_proxy"] = reported.fillna(0) - finalised.fillna(0)
        result["finalisation_ratio"] = safe_divide(finalised, reported)
    if incurred is not None and reported is not None:
        result["average_incurred_per_reported_claim"] = safe_divide(incurred, reported)
    if paid is not None and finalised is not None:
        result["average_paid_per_finalised_claim"] = safe_divide(paid, finalised)
    if paid is not None and incurred is not None:
        result["payment_to_incurred_ratio"] = safe_divide(paid, incurred)
        result["outstanding_incurred_proxy"] = incurred - paid
    if {"reported_year", "accident_year"} <= set(result):
        result["reporting_lag"] = result["reported_year"] - result["accident_year"]
    if {"finalised_year", "reported_year"} <= set(result):
        result["finalisation_lag"] = result["finalised_year"] - result["reported_year"]
    return result


def aggregate_claims(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    columns = [
        column
        for column in [
            "number_of_claims_reported1",
            "number_of_claims_finalised",
            "gross_claim_payments",
            "gross_claims_incurred",
        ]
        if column in frame
    ]
    grouped = frame.groupby(groups, dropna=False)[columns].sum(min_count=1).reset_index()
    return add_claim_metrics(grouped)


def add_policy_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if {"gross_earned_premium", "risk_in_force_weighted"} <= set(result):
        result["average_earned_premium_per_risk"] = safe_divide(
            result["gross_earned_premium"], result["risk_in_force_weighted"]
        )
    return result
