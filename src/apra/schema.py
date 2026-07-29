"""Observed APRA schema contracts."""

from __future__ import annotations

YEAR_COLUMNS = [
    "reporting_year",
    "underwriting_year",
    "accident_year",
    "reported_year",
    "finalised_year",
]

NUMERIC_COLUMNS = [
    "risk_in_force_weighted",
    "number_of_risks_written1",
    "gross_earned_premium",
    "gross_written_premium_1",
    "number_of_claims_reported1",
    "number_of_claims_finalised",
    "gross_claim_payments",
    "gross_claims_incurred",
]

CATEGORY_COLUMNS = [
    "product_type",
    "class_of_business",
    "state_jurisdiction",
    "industry_occupation_group",
    "excess_deductible_band",
    "limit_of_indemnity_band",
]

KNOWN_STATES = {"ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"}


def classify_report(filename: str) -> tuple[str, str, str]:
    lower = filename.lower()
    report_type = "claims" if "claim" in lower else "policies"
    geography = "state" if "state" in lower else "occupation"
    band = "eda" if "eda" in lower else "loi"
    return report_type, geography, band


def table_name(filename: str) -> str:
    report_type, geography, band = classify_report(filename)
    return f"{report_type}_by_{geography}_{band}"
