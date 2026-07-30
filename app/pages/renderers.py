"""Page render functions with explicit analytical scope."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.charts import line, ranked_bar
from components.filters import apply_apra_filters
from components.kpi_cards import kpi_row
from components.warnings import apra_scope_warning, french_disclaimer

from config import APRA_SOURCE_NOTE, FRENCH_SOURCE_NOTE
from data import apra_table, french_table, read_json
from src.apra.development import development_matrix
from src.apra.metrics import aggregate_claims
from src.apra.scenarios import Scenario, calculate_scenario
from src.config import settings
from src.fremtpl2.premium import Loadings, calculate_loaded_premium


def _empty(message: str = "Run the relevant build pipeline to populate this page.") -> None:
    st.info(message)
    st.stop()


def _apra_claims(basis: str = "claims_by_state_loi") -> pd.DataFrame:
    st.caption(f"Analytical basis: `{basis}` — no other APRA report cut is added.")
    frame = apra_table(basis)
    if frame.empty:
        _empty()
    return apply_apra_filters(frame)


def _apra_policy(basis: str = "policies_by_state_loi") -> pd.DataFrame:
    st.caption(f"Analytical basis: `{basis}` — no other APRA report cut is added.")
    frame = apra_table(basis)
    if frame.empty:
        _empty()
    return apply_apra_filters(frame)


def render_apra_overview() -> None:
    st.title("Australian APRA Portfolio Overview")
    apra_scope_warning()
    claims = _apra_claims()
    if claims.empty:
        _empty("No rows match the selected filters.")
    totals = claims[
        [
            "number_of_claims_reported1",
            "number_of_claims_finalised",
            "gross_claim_payments",
            "gross_claims_incurred",
        ]
    ].sum()
    finalisation = (
        totals["number_of_claims_finalised"] / totals["number_of_claims_reported1"]
        if totals["number_of_claims_reported1"]
        else np.nan
    )
    severity = (
        totals["gross_claims_incurred"] / totals["number_of_claims_reported1"]
        if totals["number_of_claims_reported1"]
        else np.nan
    )
    kpi_row(
        [
            ("Claims reported", f"{totals['number_of_claims_reported1']:,.0f}", None),
            ("Claims finalised", f"{totals['number_of_claims_finalised']:,.0f}", None),
            ("Gross incurred", f"A${totals['gross_claims_incurred']:,.0f}", None),
            ("Gross payments", f"A${totals['gross_claim_payments']:,.0f}", None),
            ("Average incurred", f"A${severity:,.0f}", "Per reported claim"),
            ("Finalisation ratio", f"{finalisation:.1%}", "Finalised / reported"),
        ]
    )
    trend = aggregate_claims(claims, ["reporting_year"])
    line(trend, "reporting_year", "gross_claims_incurred", "Incurred claims by reporting year", "A$")
    st.caption(APRA_SOURCE_NOTE)


def render_policy_trends() -> None:
    st.title("APRA Policy Trends")
    apra_scope_warning()
    frame = _apra_policy()
    trend = (
        frame.groupby("reporting_year", as_index=False)[["risk_in_force_weighted", "gross_earned_premium"]]
        .sum(min_count=1)
        .sort_values("reporting_year")
    )
    trend["exposure_growth"] = trend["risk_in_force_weighted"].pct_change()
    trend["premium_growth"] = trend["gross_earned_premium"].pct_change()
    line(trend, "reporting_year", "risk_in_force_weighted", "Weighted risk in force", "Exposure")
    line(trend, "reporting_year", "gross_earned_premium", "Gross earned premium", "A$")
    st.dataframe(trend, width="stretch")
    st.caption("Risks written and written premium are omitted where source values are missing.")
    st.caption(APRA_SOURCE_NOTE)


def render_claims_trends() -> None:
    st.title("APRA Claims Trends")
    apra_scope_warning()
    frame = _apra_claims()
    trend = aggregate_claims(frame, ["reporting_year"])
    for column in ["number_of_claims_reported1", "gross_claims_incurred", "gross_claim_payments"]:
        trend[f"{column}_yoy"] = trend[column].pct_change()
    figure = px.line(
        trend,
        x="reporting_year",
        y=["gross_claims_incurred", "gross_claim_payments"],
        markers=True,
        title="Gross incurred and paid movements",
        labels={"value": "A$", "variable": "Measure"},
    )
    st.plotly_chart(figure, width="stretch")
    st.dataframe(trend, width="stretch")
    st.caption(APRA_SOURCE_NOTE)


def render_severity() -> None:
    st.title("APRA Severity Analysis")
    apra_scope_warning()
    basis = st.selectbox(
        "Segment basis",
        ["claims_by_state_loi", "claims_by_state_eda", "claims_by_occupation_loi", "claims_by_occupation_eda"],
    )
    frame = _apra_claims(basis)
    dimension = "state_jurisdiction" if "state_jurisdiction" in frame else "industry_occupation_group"
    summary = aggregate_claims(frame, [dimension])
    ranked_bar(
        summary.dropna(subset=["average_incurred_per_reported_claim"]),
        dimension,
        "average_incurred_per_reported_claim",
        "Average incurred severity by segment",
        "A$ per reported claim",
    )
    st.caption(APRA_SOURCE_NOTE)


def render_development() -> None:
    st.title("APRA Claims Development")
    apra_scope_warning()
    frame = _apra_claims()
    value = st.selectbox("Development measure", ["gross_claims_incurred", "gross_claim_payments"])
    matrix = development_matrix(frame, value=value)
    if matrix.empty:
        _empty("The selected filters do not support a development matrix.")
    figure = px.imshow(
        matrix,
        aspect="auto",
        color_continuous_scale="RdBu",
        title="Illustrative accident-year development matrix",
        labels={"x": "Development period", "y": "Accident year", "color": "A$"},
    )
    st.plotly_chart(figure, width="stretch")
    st.warning("This descriptive matrix is not a production reserve or chain-ladder estimate.")
    st.caption(APRA_SOURCE_NOTE)


def render_segment_explorer() -> None:
    st.title("APRA Segment Explorer")
    apra_scope_warning()
    basis = st.selectbox(
        "Report basis",
        ["claims_by_state_loi", "claims_by_state_eda", "claims_by_occupation_loi", "claims_by_occupation_eda"],
    )
    frame = _apra_claims(basis)
    choices = [
        column
        for column in ["state_jurisdiction", "industry_occupation_group", "product_type", "class_of_business"]
        if column in frame
    ]
    dimension = st.selectbox("Dimension", choices)
    summary = aggregate_claims(frame, [dimension]).dropna(subset=["average_incurred_per_reported_claim"])
    figure = px.scatter(
        summary,
        x="number_of_claims_reported1",
        y="average_incurred_per_reported_claim",
        size=summary["gross_claims_incurred"].abs().clip(lower=1),
        color=dimension,
        hover_name=dimension,
        title="Volume versus severity",
        labels={
            "number_of_claims_reported1": "Reported claims",
            "average_incurred_per_reported_claim": "A$ per reported claim",
        },
    )
    st.plotly_chart(figure, width="stretch")
    st.caption(APRA_SOURCE_NOTE)


def render_apra_scenarios() -> None:
    st.title("APRA Portfolio Pricing Scenario")
    apra_scope_warning()
    st.caption("Claims-cost index only. No fictional dollar premium is generated.")
    columns = st.columns(3)
    inputs = Scenario(
        severity_trend=columns[0].slider("Severity trend", -0.2, 0.4, 0.05),
        frequency_trend=columns[1].slider("Claim count / frequency trend", -0.2, 0.4, 0.02),
        inflation=columns[2].slider("Inflation", -0.1, 0.3, 0.03),
        expense_change=columns[0].slider("Expense change", -0.1, 0.3, 0.0),
        risk_margin=columns[1].slider("Risk margin", 0.0, 0.3, 0.02),
        target_margin=columns[2].slider("Target margin", 0.0, 0.3, 0.05),
        credibility=columns[0].slider("Credibility", 0.0, 1.0, 1.0),
        management_adjustment=columns[1].slider("Management adjustment", -0.2, 0.2, 0.0),
    )
    result = calculate_scenario(inputs)
    st.metric("Simulated rate-change recommendation", f"{result['simulated_rate_change']:.1%}")
    st.code(
        "Stressed cost = 100 × (1 + severity trend) × (1 + frequency trend)\n"
        "Technical indication = stressed cost × (1 + inflation) × "
        "(1 + expense change + risk margin)\n"
        "Margin indication = technical indication ÷ (1 - target margin)"
    )
    st.dataframe(pd.DataFrame([result]).T.rename(columns={0: "value"}), width="stretch")


def render_apra_quality() -> None:
    st.title("APRA Data Quality")
    apra_scope_warning()
    basis = st.selectbox(
        "Table",
        [
            "claims_by_state_loi",
            "claims_by_state_eda",
            "claims_by_occupation_loi",
            "claims_by_occupation_eda",
            "policies_by_state_loi",
            "policies_by_state_eda",
            "policies_by_occupation_loi",
            "policies_by_occupation_eda",
        ],
    )
    frame = apra_table(basis)
    if frame.empty:
        _empty()
    flags = [column for column in frame if column.startswith("is_")]
    summary = pd.DataFrame({"check": flags, "exceptions": [int(frame[column].sum()) for column in flags]})
    st.dataframe(summary, width="stretch")
    exceptions = frame.loc[frame[flags].any(axis=1)]
    st.download_button(
        "Download exception report",
        exceptions.to_csv(index=False),
        file_name=f"{basis}_exceptions.csv",
        mime="text/csv",
    )
    st.caption("Negative values are preserved and flagged; missing values are not replaced with zero.")


def _french_ready() -> None:
    french_disclaimer()
    if not settings.enable_french_module:
        _empty("French module is disabled by ENABLE_FRENCH_MODULE=false.")


def render_french_overview() -> None:
    st.title("French Dataset Overview")
    _french_ready()
    frequency = french_table("fremtpl2_frequency")
    severity = french_table("fremtpl2_severity")
    audit = read_json(settings.french_processed / "ingestion_audit.json")
    if frequency.empty:
        _empty()
    kpi_row(
        [
            ("Policies", f"{audit.get('frequency_rows', len(frequency)):,}", None),
            ("Claim records", f"{audit.get('severity_rows', len(severity)):,}", None),
            (
                "Exposure",
                f"{audit.get('total_exposure', frequency['Exposure'].sum()):,.0f}",
                "Policy-year exposure",
            ),
            ("Claims", f"{audit.get('total_claims', frequency['ClaimNb'].sum()):,.0f}", None),
        ]
    )
    st.plotly_chart(px.histogram(frequency, x="DrivAge", title="Driver age distribution"), width="stretch")
    st.caption(FRENCH_SOURCE_NOTE)


def render_frequency_model() -> None:
    st.title("Frequency Model")
    _french_ready()
    metrics = read_json(settings.french_processed / "frequency_model_metrics.json")
    if not metrics:
        _empty()
    st.json(metrics)
    calibration = french_table("frequency_calibration")
    st.plotly_chart(
        px.line(
            calibration,
            x="predicted",
            y="observed",
            markers=True,
            title="Observed versus predicted frequency by decile",
        ),
        width="stretch",
    )
    st.dataframe(french_table("frequency_coefficients"), width="stretch")


def render_severity_model() -> None:
    st.title("Severity Model")
    _french_ready()
    metrics = read_json(settings.french_processed / "severity_model_metrics.json")
    if not metrics:
        _empty()
    st.json(metrics)
    calibration = french_table("severity_calibration")
    st.plotly_chart(
        px.line(
            calibration, x="predicted", y="observed", markers=True, title="Observed versus predicted severity by decile"
        ),
        width="stretch",
    )
    st.caption("All positive claims are retained; no cap or winsorisation is applied.")


def render_risk_segmentation() -> None:
    st.title("Risk Segmentation")
    _french_ready()
    predictions = french_table("frequency_predictions")
    if predictions.empty:
        _empty()
    predictions["risk_decile"] = pd.qcut(predictions["predicted_frequency"].rank(method="first"), 10, labels=False) + 1
    summary = predictions.groupby("risk_decile", as_index=False).agg(
        exposure=("Exposure", "sum"),
        claims=("ClaimNb", "sum"),
        predicted_claims=("predicted_claim_count", "sum"),
    )
    summary["observed_frequency"] = summary["claims"] / summary["exposure"]
    summary["predicted_frequency"] = summary["predicted_claims"] / summary["exposure"]
    st.plotly_chart(
        px.bar(
            summary,
            x="risk_decile",
            y=["observed_frequency", "predicted_frequency"],
            barmode="group",
            title="Frequency lift by risk decile",
        ),
        width="stretch",
    )
    st.dataframe(summary, width="stretch")


def _sample_policy() -> pd.Series:
    frame = french_table("fremtpl2_frequency")
    if frame.empty:
        _empty()
    return frame.iloc[0]


def render_technical_premium() -> None:
    st.title("Estimated Technical Claims Cost")
    _french_ready()
    frequency = read_json(settings.french_processed / "frequency_model_metrics.json")
    severity = read_json(settings.french_processed / "severity_model_metrics.json")
    if not frequency or not severity:
        _empty()
    estimate = frequency["predicted_frequency"] * severity["predicted_mean"]
    kpi_row(
        [
            ("Estimated frequency", f"{frequency['predicted_frequency']:.4f}", "Claims per exposure"),
            ("Estimated severity", f"€{severity['predicted_mean']:,.2f}", "Mean held-out prediction"),
            ("Technical claims cost", f"€{estimate:,.2f}", "Frequency × severity"),
        ]
    )
    st.info("This is a pure-premium estimate, not a final customer premium.")


def render_premium_simulator() -> None:
    st.title("Premium Loading Simulator")
    _french_ready()
    frequency = read_json(settings.french_processed / "frequency_model_metrics.json")
    severity = read_json(settings.french_processed / "severity_model_metrics.json")
    if not frequency or not severity:
        _empty()
    claims_cost = frequency["predicted_frequency"] * severity["predicted_mean"]
    loadings = Loadings(
        expense=st.slider("Expense loading", 0.0, 0.5, 0.15),
        commission=st.slider("Commission", 0.0, 0.5, 0.10),
        risk_margin=st.slider("Risk margin", 0.0, 0.5, 0.05),
        profit_margin=st.slider("Profit margin", 0.0, 0.3, 0.05),
        tax_or_levy=st.slider("Tax / levy assumption", 0.0, 0.3, 0.10),
        reinsurance=st.slider("Reinsurance loading", 0.0, 0.3, 0.03),
        management_adjustment=st.slider("Management adjustment", -0.3, 0.3, 0.0),
    )
    result = calculate_loaded_premium(claims_cost, loadings)
    st.metric("Simulated indicated premium", f"€{result['simulated_indicated_premium']:,.2f}")
    labels = ["Technical claims cost", "Cost loadings", "Profit margin", "Tax", "Management"]
    values = [
        claims_cost,
        result["subtotal_after_cost_loadings"] - claims_cost,
        result["premium_before_tax"] - result["subtotal_after_cost_loadings"],
        result["premium_before_tax"] * loadings.tax_or_levy,
        result["simulated_indicated_premium"] - result["premium_before_tax"] * (1 + loadings.tax_or_levy),
    ]
    figure = go.Figure(
        go.Waterfall(x=labels, y=values, measure=["absolute", "relative", "relative", "relative", "relative"])
    )
    figure.update_layout(title="Simulated premium build-up", yaxis_title="€")
    st.plotly_chart(figure, width="stretch")
    st.code(
        "Technical claims cost = expected frequency × expected severity\n"
        "Before tax = claims cost × (1 + expense + commission + risk + reinsurance) "
        "÷ (1 - profit margin)\n"
        "Indicated premium = before tax × (1 + tax) × (1 + management adjustment)"
    )


def render_governance() -> None:
    st.title("Methodology and Model Governance")
    french_disclaimer()
    st.markdown(
        """
        **Separation:** APRA aggregates are used only for Australian descriptive analytics.
        freMTPL2 is used only for educational policy-level modelling.

        **Leakage:** Policy ID supports joins and deterministic split checks but is excluded from
        every model formula. Frequency uses `log(exposure)` as an offset. Severity uses positive
        claim amounts and retains large losses.

        **Interpretation:** APRA trends are descriptive and do not imply causation. Development
        matrices are educational, not reserve estimates. French technical claims cost is not a
        final customer premium or an Australian market indication.
        """
    )
