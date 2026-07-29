"""KPI card layout."""

from collections.abc import Iterable

import streamlit as st


def kpi_row(items: Iterable[tuple[str, str, str | None]]) -> None:
    values = list(items)
    columns = st.columns(len(values))
    for column, (label, value, help_text) in zip(columns, values, strict=True):
        column.metric(label, value, help=help_text)
