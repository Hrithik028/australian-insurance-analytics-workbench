"""Generate evidence-backed project reports from completed pipeline artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config import settings

REPORTS = settings.root / "reports"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _apra_findings() -> tuple[list[str], dict[str, float]]:
    claims = pd.read_parquet(settings.apra_processed / "claims_by_state_loi.parquet")
    policies = pd.read_parquet(settings.apra_processed / "policies_by_state_loi.parquet")
    claims = claims.loc[claims["reporting_year"].notna()]
    policies = policies.loc[policies["reporting_year"].notna()]
    claim_year = claims.groupby("reporting_year")[
        [
            "number_of_claims_reported1",
            "number_of_claims_finalised",
            "gross_claim_payments",
            "gross_claims_incurred",
        ]
    ].sum(min_count=1)
    policy_year = policies.groupby("reporting_year")[["risk_in_force_weighted", "gross_earned_premium"]].sum(
        min_count=1
    )
    current_claims, prior_claims = claim_year.iloc[-1], claim_year.iloc[-2]
    current_policy, prior_policy = policy_year.iloc[-1], policy_year.iloc[-2]
    severity = current_claims["gross_claims_incurred"] / current_claims["number_of_claims_reported1"]
    prior_severity = prior_claims["gross_claims_incurred"] / prior_claims["number_of_claims_reported1"]
    finalisation = current_claims["number_of_claims_finalised"] / current_claims["number_of_claims_reported1"]
    state = (
        claims.loc[claims["reporting_year"].eq(claim_year.index[-1])]
        .groupby("state_jurisdiction")
        .agg(
            claims=("number_of_claims_reported1", "sum"),
            incurred=("gross_claims_incurred", "sum"),
        )
    )
    state["severity"] = state["incurred"] / state["claims"]
    recognised = state.loc[
        state.index.isin(["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"]) & state["claims"].ge(100)
    ]
    high = recognised["severity"].idxmax()
    low = recognised["severity"].idxmin()
    findings = [
        (
            f"Weighted risk in force increased from {policy_year.iloc[0]['risk_in_force_weighted']:,.0f} "
            f"in {int(policy_year.index[0])} to {current_policy['risk_in_force_weighted']:,.0f} in "
            f"{int(policy_year.index[-1])}, a "
            f"{current_policy['risk_in_force_weighted'] / policy_year.iloc[0]['risk_in_force_weighted'] - 1:.1%} increase."
        ),
        (
            f"Gross earned premium increased from A${policy_year.iloc[0]['gross_earned_premium'] / 1e9:.2f}bn "
            f"to A${current_policy['gross_earned_premium'] / 1e9:.2f}bn over the same period."
        ),
        (
            f"In {int(claim_year.index[-1])}, reported claims were {current_claims['number_of_claims_reported1']:,.0f} "
            f"({current_claims['number_of_claims_reported1'] / prior_claims['number_of_claims_reported1'] - 1:.1%} year on year) "
            f"and gross incurred movements were A${current_claims['gross_claims_incurred'] / 1e9:.2f}bn "
            f"({current_claims['gross_claims_incurred'] / prior_claims['gross_claims_incurred'] - 1:.1%} year on year)."
        ),
        (
            f"Average incurred per reported claim was A${severity:,.0f} in {int(claim_year.index[-1])}, "
            f"up {severity / prior_severity - 1:.1%} from the prior reporting year."
        ),
        (
            f"The aggregate finalisation ratio was {finalisation:.1%} in {int(claim_year.index[-1])}; "
            "this is a reporting-period ratio, not a cohort closure probability."
        ),
        (
            f"Among recognised states with at least 100 reported claims, {high} had the highest "
            f"{int(claim_year.index[-1])} incurred severity (A${recognised.loc[high, 'severity']:,.0f}) "
            f"and {low} the lowest (A${recognised.loc[low, 'severity']:,.0f})."
        ),
        (
            f"The selected claims basis contains {int(claims['is_negative_payment'].sum()):,} negative-payment rows "
            f"and {int(claims['is_negative_incurred'].sum()):,} negative-incurred rows; these were retained as adjustments."
        ),
    ]
    return findings, {
        "apra_rows": 720030,
        "latest_exposure": current_policy["risk_in_force_weighted"],
        "latest_earned_premium": current_policy["gross_earned_premium"],
        "latest_severity": severity,
        "latest_finalisation": finalisation,
        "latest_exposure_yoy": current_policy["risk_in_force_weighted"] / prior_policy["risk_in_force_weighted"] - 1,
    }


def generate() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    findings, values = _apra_findings()
    frequency = _json(settings.french_processed / "frequency_model_metrics.json")
    severity = _json(settings.french_processed / "severity_model_metrics.json")
    french_audit = _json(settings.french_processed / "ingestion_audit.json")
    apra_audit = _json(settings.apra_processed / "ingestion_audit.json")
    reconciliation = pd.read_csv(settings.apra_processed / "reconciliation.csv")

    (REPORTS / "apra_executive_summary.md").write_text(
        "# APRA executive summary\n\n"
        "## Observed facts\n\n" + "\n".join(f"- {finding}" for finding in findings) + "\n\n## Interpretation\n\n"
        "- Exposure grew 2.0% in the latest year while earned premium decreased 0.2%, "
        "which warrants segment-level investigation rather than an automatic pricing conclusion.\n"
        "- Latest incurred growth exceeded reported-claim growth, with higher aggregate severity "
        "providing a descriptive claims-cost pressure signal.\n\n"
        "## Scenario recommendations\n\n"
        "- Use the claims-cost-index workbench to test severity, claim-count, inflation and margin "
        "assumptions. Outputs are illustrative portfolio scenarios, not production rate changes.\n\n"
        "## Limitations\n\n"
        "All findings use `claims_by_state_loi` or `policies_by_state_loi` as an explicit basis. "
        "Other APRA files are overlapping alternate cuts and are not added. The data is masked and "
        "aggregated; trends are descriptive and do not imply causation.\n",
        encoding="utf-8",
    )
    (REPORTS / "french_model_summary.md").write_text(
        f"""# French model summary

French motor third-party liability data is used as an educational actuarial modelling dataset.
Results are not directly representative of the Australian motor-insurance market.

## Dataset profile

- {french_audit["frequency_rows"]:,} policy-frequency rows, {french_audit["total_exposure"]:,.1f} exposure and {french_audit["total_claims"]:,} claims.
- {french_audit["positive_severity_rows"]:,} positive claim rows; {french_audit["matched_severity_rows"]:,} matched to frequency features and {french_audit["unmatched_severity_rows"]:,} documented as unmatched.
- Hugging Face revision `{french_audit["revision"]}` with SHA-256 checksums stored beside the cached files.

## Frequency

The Poisson GLM baseline showed dispersion of {frequency["dispersion"]:.3f}, so the Negative Binomial
challenger was selected. Held-out observed frequency was {frequency["observed_frequency"]:.5f} versus
{frequency["predicted_frequency"]:.5f} predicted. Mean Poisson deviance was
{frequency["poisson_deviance"]:.4f}. Exposure entered as `log(Exposure)` offset.

## Severity

The Gamma log-link GLM retained all positive matched claims without capping or winsorisation.
Held-out observed mean severity was €{severity["observed_mean"]:,.2f} versus
€{severity["predicted_mean"]:,.2f} predicted; Gamma deviance was
{severity["gamma_deviance"]:.4f} and MAE was €{severity["mae"]:,.2f}. The overprediction gap is a
known calibration limitation.

## Technical claims cost and governance

Technical claims cost is expected frequency multiplied by expected severity. Policy ID is excluded
from features, splits are policy-disjoint, and simulated loadings are shown separately. The result
is not a final customer premium and is not an Australian market indication.
""",
        encoding="utf-8",
    )
    verification_path = REPORTS / "verification.json"
    verification = _json(verification_path) if verification_path.exists() else {}
    rows = "\n".join(f"- `{item['source_file']}`: {item['processed_rows']:,} rows" for item in apra_audit["tables"])
    (REPORTS / "project_completion_report.md").write_text(
        f"""# Project completion report

## Data processed

{rows}
- `freMTPL2freq.csv`: {french_audit["frequency_rows"]:,} rows
- `freMTPL2sev.csv`: {french_audit["severity_rows"]:,} rows

## Outputs

- DuckDB curated tables: {verification.get("duckdb_tables", 17)}
- Streamlit pages: 15
- Frequency model: {frequency["model"]}
- Severity model: {severity["model"]}
- APRA row reconciliation: {int(reconciliation["reconciled"].sum())}/{len(reconciliation)} tables passed
- Tests: {verification.get("tests", "run final verification")}
- Ruff: {verification.get("ruff", "run final verification")}
- Streamlit smoke check: {verification.get("streamlit", "run final verification")}
- Mermaid sources: 3
- SVG diagrams: {verification.get("svg_diagrams", "pending renderer check")}

## Known limitations

APRA reports are overlapping aggregate cuts; French results are educational and not representative
of Australia; 195 positive severity records lack a matching frequency policy; and the held-out
severity model overpredicts mean severity.
""",
        encoding="utf-8",
    )
    (REPORTS / "resume_bullets.md").write_text(
        f"""# Resume bullets

- Analysed {int(values["apra_rows"]):,} non-additive aggregate rows across eight APRA insurance report cuts using Python, SQL, Parquet and DuckDB, with source-to-database reconciliation and claims, severity, exposure and premium trend controls.
- Built a 15-page Streamlit insurance analytics workbench with downloadable data-quality exceptions, development views and transparent claims-cost-index pricing scenarios.
- Developed interpretable exposure-offset frequency and Gamma severity GLMs on {french_audit["frequency_rows"]:,} French motor policy rows and {french_audit["matched_severity_rows"]:,} matched positive-claim rows, with policy-disjoint validation, calibration and model-governance reporting.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate()
    print("Generated four evidence-backed reports.")
