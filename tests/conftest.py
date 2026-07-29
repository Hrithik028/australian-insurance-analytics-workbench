"""Synthetic fixtures only; source datasets are never loaded in tests."""

import pandas as pd
import pytest


@pytest.fixture
def claim_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "reporting_year": [2023, 2024, 2024],
            "accident_year": [2022, 2024, 2025],
            "reported_year": [2023, 2024, 2024],
            "finalised_year": [2024, 2023, 2024],
            "state_jurisdiction": ["NSW", "unknown", "XX"],
            "number_of_claims_reported1": [10.0, 0.0, 2.0],
            "number_of_claims_finalised": [5.0, 1.0, 3.0],
            "gross_claim_payments": [100.0, -25.0, 5.0],
            "gross_claims_incurred": [200.0, -10.0, 0.0],
        }
    )
