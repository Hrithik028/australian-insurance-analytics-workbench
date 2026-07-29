"""Data-aware APRA filters."""

import pandas as pd
import streamlit as st


def apply_apra_filters(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame
    labels = {
        "reporting_year": "Reporting year",
        "state_jurisdiction": "State / jurisdiction",
        "industry_occupation_group": "Occupation group",
        "product_type": "Product type",
        "class_of_business": "Class of business",
        "excess_deductible_band": "Excess band",
        "limit_of_indemnity_band": "Indemnity limit",
    }
    with st.sidebar:
        st.subheader("Filters")
        for column, label in labels.items():
            if column not in result:
                continue
            options = sorted(result[column].dropna().unique().tolist(), key=str)
            selected = st.multiselect(label, options)
            if selected:
                result = result.loc[result[column].isin(selected)]
    return result
