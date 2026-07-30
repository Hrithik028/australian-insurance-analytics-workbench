"""Recruiter-friendly project landing page."""

from __future__ import annotations

import streamlit as st

from data import read_json, using_demo_data
from src.config import settings
from src.fremtpl2 import DISCLAIMER


def _metric_value(payload: dict, key: str, fallback: str) -> str:
    value = payload.get(key)
    return fallback if value is None else f"{value:,}"


def _answer(question: str, answer: str) -> None:
    with st.expander(question):
        st.markdown(answer)


def render_home() -> None:
    french_audit = read_json(settings.french_processed / "ingestion_audit.json")
    frequency = read_json(settings.french_processed / "frequency_model_metrics.json")
    severity = read_json(settings.french_processed / "severity_model_metrics.json")
    apra_audit = read_json(settings.apra_processed / "ingestion_audit.json")
    verification = read_json(settings.root / "reports/verification.json")
    apra_rows = sum(item.get("processed_rows", 0) for item in apra_audit.get("tables", []))

    if using_demo_data():
        st.info(
            "Public demo mode: charts use compact derived artifacts committed for deployment. "
            "Verified project totals come from the full pipeline audits."
        )

    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1240px;}
        .hero {
            padding: 2.7rem 3rem;
            border-radius: 24px;
            background:
                radial-gradient(circle at 90% 15%, rgba(56,189,248,.28), transparent 30%),
                linear-gradient(135deg, #0f172a 0%, #172554 54%, #0c4a6e 100%);
            color: white;
            box-shadow: 0 18px 50px rgba(15,23,42,.22);
            margin-bottom: 1.4rem;
        }
        .hero-kicker {
            display: inline-block;
            padding: .35rem .75rem;
            border: 1px solid rgba(255,255,255,.3);
            border-radius: 999px;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }
        .hero h1 {font-size: 2.65rem; line-height: 1.08; margin: 0 0 .8rem;}
        .hero p {font-size: 1.05rem; line-height: 1.7; max-width: 850px; color: #dbeafe;}
        .hero-stack {margin-top: 1.15rem; color: #bae6fd; font-weight: 600;}
        .section-label {
            color: #0369a1;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .11em;
            text-transform: uppercase;
            margin-bottom: .25rem;
        }
        .project-card {
            min-height: 210px;
            padding: 1.25rem;
            border: 1px solid rgba(14,116,144,.2);
            border-radius: 16px;
            background: rgba(14,116,144,.055);
        }
        .project-card h3 {font-size: 1.03rem; margin: 0 0 .55rem;}
        .project-card p {font-size: .91rem; line-height: 1.55; margin-bottom: 0;}
        .pipeline {
            padding: 1.25rem 1.35rem;
            border-radius: 16px;
            border: 1px solid rgba(100,116,139,.22);
            min-height: 225px;
        }
        .verified {
            padding: 1.2rem 1.4rem;
            border-left: 5px solid #0284c7;
            border-radius: 10px;
            background: rgba(2,132,199,.07);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="hero">
          <div class="hero-kicker">Insurance analytics portfolio project</div>
          <h1>Australian Insurance Portfolio Analytics<br>and Pricing Workbench</h1>
          <p>
            An end-to-end demonstration of how I inspect insurance data, build reliable analytical
            pipelines, investigate claims and portfolio performance, develop interpretable pricing
            models, and communicate limitations to business stakeholders.
          </p>
          <div class="hero-stack">
            Python · Pandas · DuckDB · SQL · Statsmodels GLMs · Plotly · Streamlit
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    intro_left, intro_right = st.columns([1.45, 1], gap="large")
    with intro_left:
        st.markdown('<div class="section-label">Start here</div>', unsafe_allow_html=True)
        st.subheader("What this project demonstrates")
        st.write(
            "I built two deliberately separate analytical modules: Australian portfolio analytics "
            "from APRA masked aggregate reports, and educational motor pricing models from the "
            "French freMTPL2 policy dataset. The workbench brings them into one application without "
            "merging the datasets or presenting French results as Australian market evidence."
        )
    with intro_right:
        st.markdown('<div class="section-label">Suggested walkthrough</div>', unsafe_allow_html=True)
        st.markdown(
            """
            1. [🇦🇺 Explore the APRA portfolio](APRA_Portfolio_Overview)
            2. [📈 Review the frequency model](Frequency_Model)
            3. [🧮 Test the premium simulator](Premium_Simulator)
            4. [🛡️ Check governance and limitations](Model_Governance)
            """
        )

    st.divider()
    st.markdown('<div class="section-label">Verified project scale</div>', unsafe_allow_html=True)
    metric_columns = st.columns(4)
    metric_columns[0].metric("APRA aggregate rows", f"{apra_rows or 720_030:,}")
    metric_columns[1].metric(
        "French policy rows",
        _metric_value(french_audit, "frequency_rows", "678,013"),
    )
    metric_columns[2].metric("Interactive pages", "16", help="Home plus 15 analytical pages")
    metric_columns[3].metric("Automated tests", verification.get("tests", "20 passed"))
    st.caption("APRA row counts describe eight overlapping report cuts and are not an additive policy count.")

    st.divider()
    st.markdown('<div class="section-label">What I have done</div>', unsafe_allow_html=True)
    st.header("From raw files to an interview-ready analytical product")
    cards = st.columns(4, gap="medium")
    card_content = [
        (
            "1 · Data engineering",
            "Safely extracted eight APRA workbooks, inspected every worksheet, preserved raw values, "
            "standardised schemas, added source lineage, wrote Parquet outputs and loaded DuckDB.",
        ),
        (
            "2 · Portfolio analytics",
            "Built claims, severity, policy, exposure, premium, development, segment and scenario "
            "views while preventing cross-report double counting and unsafe denominator use.",
        ),
        (
            "3 · Pricing modelling",
            "Developed an exposure-offset frequency GLM and a Gamma severity GLM, then combined their "
            "estimates into a transparent technical claims-cost and loading simulator.",
        ),
        (
            "4 · Quality and governance",
            "Added exception flags, checksum and schema controls, leakage-safe splits, calibration "
            "diagnostics, SQL reconciliation, automated tests, documentation and explicit limitations.",
        ),
    ]
    for column, (title, description) in zip(cards, card_content, strict=True):
        with column:
            st.markdown(
                f'<div class="project-card"><h3>{title}</h3><p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown('<div class="section-label">Analytical design</div>', unsafe_allow_html=True)
    st.header("Two pipelines, one governed workbench")
    australian, french = st.columns(2, gap="large")
    with australian:
        st.markdown(
            """
            <div class="pipeline">
              <h3>🇦🇺 Australian APRA portfolio analytics</h3>
              <p><strong>Purpose:</strong> descriptive portfolio, claims and pricing-scenario analysis.</p>
              <p><strong>Data:</strong> masked aggregate policy and claims reports.</p>
              <p><strong>Outputs:</strong> exposure, earned premium, claim volume, severity,
              development, segment comparison and quality exceptions.</p>
              <p><strong>Key control:</strong> each state, occupation, excess or indemnity report
              is treated as an overlapping alternative view—not summed with another report.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with french:
        st.markdown(
            """
            <div class="pipeline">
              <h3>🇫🇷 French motor pricing models</h3>
              <p><strong>Purpose:</strong> educational policy-level pricing methodology.</p>
              <p><strong>Data:</strong> public freMTPL2 frequency and severity files.</p>
              <p><strong>Outputs:</strong> expected frequency, expected severity, risk deciles,
              technical claims cost and simulated premium loadings.</p>
              <p><strong>Key control:</strong> policy ID supports joins and split checks only;
              it is excluded from every model formula.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.warning(DISCLAIMER)

    st.divider()
    st.markdown('<div class="section-label">Evidence</div>', unsafe_allow_html=True)
    st.header("Verified results at a glance")
    result_left, result_right = st.columns(2, gap="large")
    with result_left:
        st.subheader("APRA portfolio evidence")
        st.markdown(
            """
            - Weighted risk in force increased from **1.86 million in 2004** to **4.36 million in 2024**.
            - The selected 2024 report basis contains **43,014 reported claims** and
              **A$2.78 billion gross incurred**.
            - Average incurred was **A$64,687 per reported claim** in 2024.
            - Negative financial movements were retained and flagged instead of deleted.
            """
        )
    with result_right:
        st.subheader("French model evidence")
        observed_frequency = frequency.get("observed_frequency", 0.1010968)
        predicted_frequency = frequency.get("predicted_frequency", 0.1017938)
        gamma_deviance = severity.get("gamma_deviance", 1.5796)
        observed_severity = severity.get("observed_mean", 1953.32)
        predicted_severity = severity.get("predicted_mean", 2323.09)
        st.markdown(
            f"""
            - Frequency: **{observed_frequency:.5f} observed** vs
              **{predicted_frequency:.5f} predicted** on held-out policies.
            - Material overdispersion supported a **Negative Binomial variance structure**.
            - Severity: **€{observed_severity:,.0f} observed mean** vs
              **€{predicted_severity:,.0f} predicted mean**.
            - Held-out Gamma deviance: **{gamma_deviance:.4f}**; the severity
              overprediction is documented as a calibration limitation.
            """
        )
    st.markdown(
        """
        <div class="verified">
          <strong>How to read these results:</strong> they demonstrate reproducible analytical
          practice and model governance. They are not insurer recommendations, production reserve
          estimates, final customer premiums or claims of causation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown('<div class="section-label">Reviewer and interview guide</div>', unsafe_allow_html=True)
    st.header("Questions a reviewer is likely to ask")
    st.caption("Open any question for a concise explanation of the decision and supporting evidence.")

    _answer(
        "What business problem does this project solve?",
        "It demonstrates the full analytical workflow behind insurance portfolio monitoring and "
        "pricing: establish trustworthy data, understand exposure and claims movements, identify "
        "segments requiring investigation, model frequency and severity separately, and communicate "
        "a transparent technical indication with limitations.",
    )
    _answer(
        "Why are there Australian and French datasets?",
        "APRA provides Australian context but only as masked aggregates, so it supports portfolio "
        "analytics rather than policy-level modelling. freMTPL2 provides public policy-level motor "
        "data suitable for demonstrating GLMs. Keeping them separate avoids pretending the French "
        "model represents Australian market experience.",
    )
    _answer(
        "How did you prevent APRA double counting?",
        "Inspection showed that state, occupation, excess and indemnity-limit files are alternate "
        "marginal cuts of overlapping experience. I created a separate DuckDB table for each file, "
        "made the selected report basis visible in the UI, and use other cuts only for alternative "
        "segment views and reconciliation—not additive totals.",
    )
    _answer(
        "Which APRA metrics are safe to calculate?",
        "The application uses only observed fields and valid denominators: weighted exposure and "
        "earned premium from policy reports; reported/finalised claims, paid and incurred movements "
        "from claims reports; and safe severity/finalisation ratios. Unsupported metrics are omitted. "
        "The APRA pricing page uses an index scenario rather than inventing policy premiums.",
    )
    _answer(
        "Why use separate frequency and severity models?",
        "Claim occurrence and claim size are different processes. Frequency is modelled as claim "
        "count with log exposure as an offset. Severity is modelled only on positive claim amounts "
        "using a Gamma distribution and log link. Their product is an estimated technical claims "
        "cost, not a final customer premium.",
    )
    _answer(
        "Why was a Negative Binomial frequency model selected?",
        f"The Poisson baseline showed Pearson dispersion of **{frequency.get('dispersion', 2.51):.2f}**, "
        "indicating variance materially above the Poisson assumption. A Negative Binomial challenger "
        "was therefore retained for its variance structure. Both validation results remain available "
        "for review rather than hiding the baseline.",
    )
    _answer(
        "How did you prevent model leakage?",
        "Policy IDs are used for validated joins and to create policy-disjoint train, validation and "
        "test sets. They are not predictive features. Preprocessing is deterministic, and model "
        "performance is reported on held-out records.",
    )
    _answer(
        "What data-quality controls were implemented?",
        "Safe ZIP extraction, workbook/sheet discovery, schema mapping, missing-value checks, invalid "
        "year and sequence flags, negative financial-value flags, unknown categories, potential "
        "duplicates, exposure and claim-count validation, checksums, join coverage, source-to-Parquet-"
        "to-DuckDB reconciliation and downloadable exception reports.",
    )
    _answer(
        "What are the most important limitations?",
        "APRA data is masked and aggregated; its report cuts overlap; trends are descriptive and do "
        "not imply causation; development views are not production reserve estimates; 195 positive "
        "French severity records lack policy features; and the Gamma model overpredicts held-out mean "
        "severity. French results are not Australian pricing evidence.",
    )
    _answer(
        "How is the project reproducible and tested?",
        f"The repository includes central configuration, scripted downloads and builds, pinned source "
        f"metadata, Parquet and DuckDB outputs, 11 executable SQL analyses, synthetic tests, Ruff "
        f"formatting/linting, page-level Streamlit tests and a live health check. Current verification: "
        f"**{verification.get('tests', '20 passed')}** and "
        f"**{verification.get('ruff', 'all checks passed')}**.",
    )
    _answer(
        "What would you improve next?",
        "I would add repeated temporal validation, explicit severity recalibration, model-stability "
        "monitoring, a governed challenger such as gradient boosting, richer uncertainty intervals, "
        "and a hosted read-only demonstration using only permitted aggregate outputs.",
    )

    st.divider()
    st.markdown('<div class="section-label">Project status</div>', unsafe_allow_html=True)
    st.success(
        "Complete and reproducible: ingestion, modelling, SQL, dashboards, tests, diagrams and "
        "evidence-based reports are included. Use the sidebar to inspect each analytical module."
    )
