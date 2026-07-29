"""Plotly chart presentation standards."""

import plotly.express as px
import streamlit as st


def line(frame, x: str, y: str, title: str, y_label: str, color: str | None = None) -> None:
    figure = px.line(frame, x=x, y=y, color=color, markers=True, title=title)
    figure.update_layout(yaxis_title=y_label, xaxis_title=x.replace("_", " ").title())
    st.plotly_chart(figure, width="stretch")


def ranked_bar(frame, category: str, value: str, title: str, x_label: str) -> None:
    ordered = frame.sort_values(value).tail(20)
    figure = px.bar(ordered, x=value, y=category, orientation="h", title=title)
    figure.update_layout(xaxis_title=x_label, yaxis_title=category.replace("_", " ").title())
    st.plotly_chart(figure, width="stretch")
