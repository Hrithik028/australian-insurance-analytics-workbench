"""Unified, grouped Streamlit entry point."""

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import APP_TITLE  # noqa: E402

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.navigation(
    {
        "Project Overview": [
            st.Page("pages/00_Home.py", title="Home", icon="🏠", default=True),
        ],
        "Australian APRA Portfolio": [
            st.Page("pages/01_APRA_Portfolio_Overview.py", title="Portfolio Overview"),
            st.Page("pages/02_APRA_Policy_Trends.py", title="Policy Trends"),
            st.Page("pages/03_APRA_Claims_Trends.py", title="Claims Trends"),
            st.Page("pages/04_APRA_Severity_Analysis.py", title="Severity Analysis"),
            st.Page("pages/05_APRA_Claims_Development.py", title="Claims Development"),
            st.Page("pages/06_APRA_Segment_Explorer.py", title="Segment Explorer"),
            st.Page("pages/07_APRA_Pricing_Scenarios.py", title="Pricing Scenarios"),
            st.Page("pages/08_APRA_Data_Quality.py", title="Data Quality"),
        ],
        "French Policy Pricing": [
            st.Page("pages/09_French_Dataset_Overview.py", title="Dataset Overview"),
            st.Page("pages/10_Frequency_Model.py", title="Frequency Model"),
            st.Page("pages/11_Severity_Model.py", title="Severity Model"),
            st.Page("pages/12_Risk_Segmentation.py", title="Risk Segmentation"),
            st.Page("pages/13_Technical_Premium.py", title="Technical Premium"),
            st.Page("pages/14_Premium_Simulator.py", title="Premium Simulator"),
        ],
        "Methodology and Governance": [st.Page("pages/15_Model_Governance.py", title="Model Governance")],
    }
).run()
