"""Scope and methodology warnings."""

import streamlit as st

from src.fremtpl2 import DISCLAIMER


def apra_scope_warning() -> None:
    st.info(
        "APRA reports are masked aggregates. Alternate state/occupation and LOI/EDA "
        "tables overlap and are never added together in this application."
    )


def french_disclaimer() -> None:
    st.warning(DISCLAIMER)
