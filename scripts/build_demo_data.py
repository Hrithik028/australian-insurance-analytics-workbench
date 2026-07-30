"""Build compact, public deployment artifacts from the verified local outputs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from src.config import settings

APRA_TABLES = (
    "claims_by_occupation_eda",
    "claims_by_occupation_loi",
    "claims_by_state_eda",
    "claims_by_state_loi",
    "policies_by_occupation_eda",
    "policies_by_occupation_loi",
    "policies_by_state_eda",
    "policies_by_state_loi",
)
FLAGS = (
    "is_negative_payment",
    "is_negative_incurred",
    "is_negative_earned_premium",
    "is_missing_claim_count",
    "is_missing_policy_count",
    "is_missing_exposure",
    "is_missing_premium",
    "is_finalised_gt_reported",
    "is_invalid_year",
    "is_year_sequence_anomaly",
    "is_unknown_category",
    "is_potential_duplicate",
    "is_schema_exception",
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _build_apra() -> list[dict]:
    output = settings.demo_root / "apra"
    output.mkdir(parents=True, exist_ok=True)
    audit = json.loads((settings.apra_processed / "ingestion_audit.json").read_text(encoding="utf-8"))
    summaries: list[dict] = []

    for name in APRA_TABLES:
        source = pd.read_parquet(settings.apra_processed / f"{name}.parquet")
        is_claims = name.startswith("claims_")
        dimensions = [
            column
            for column in (
                "reporting_year",
                "accident_year",
                "product_type",
                "class_of_business",
                "state_jurisdiction",
                "industry_occupation_group",
                "excess_deductible_band",
                "limit_of_indemnity_band",
            )
            if column in source
        ]
        measures = (
            [
                "number_of_claims_reported1",
                "number_of_claims_finalised",
                "gross_claim_payments",
                "gross_claims_incurred",
            ]
            if is_claims
            else [
                "risk_in_force_weighted",
                "number_of_risks_written1",
                "gross_earned_premium",
                "gross_written_premium_1",
            ]
        )
        aggregations = {column: "sum" for column in measures}
        aggregations.update({column: "sum" for column in FLAGS if column in source})
        compact = source.groupby(dimensions, dropna=False, as_index=False).agg(aggregations)
        compact["source_report_type"] = "claims" if is_claims else "policies"
        compact["source_dimension"] = next(
            label for column, label in (("state_jurisdiction", "state"), ("industry_occupation_group", "occupation"))
            if column in compact
        )
        compact.to_parquet(output / f"{name}.parquet", index=False)
        summaries.append(
            {
                "table": name,
                "source_rows": int(len(source)),
                "demo_rows": int(len(compact)),
                "processed_rows": int(len(source)),
            }
        )

    sanitized_audit = {
        "tables": [
            {
                "table": item["table"],
                "source_file": item["source_file"],
                "source_rows": item["source_rows"],
                "processed_rows": item["processed_rows"],
                "exception_rows": item["exception_rows"],
            }
            for item in audit["tables"]
        ],
        "overlap_rule": audit["overlap_rule"],
    }
    _write_json(output / "ingestion_audit.json", sanitized_audit)
    return summaries


def _build_french() -> list[dict]:
    source = settings.french_processed
    output = settings.demo_root / "fremtpl2"
    output.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []

    frequency = pd.read_parquet(source / "fremtpl2_frequency.parquet")
    frequency_sample = frequency.sample(n=min(20_000, len(frequency)), random_state=2026)[
        ["Exposure", "ClaimNb", "DrivAge"]
    ].sort_values("DrivAge")
    frequency_sample.to_parquet(output / "fremtpl2_frequency.parquet", index=False)
    summaries.append(
        {"table": "fremtpl2_frequency", "source_rows": len(frequency), "demo_rows": len(frequency_sample)}
    )

    severity = pd.read_parquet(source / "fremtpl2_severity.parquet")
    severity_sample = severity.sample(n=min(5_000, len(severity)), random_state=2026)
    severity_sample.to_parquet(output / "fremtpl2_severity.parquet", index=False)
    summaries.append(
        {"table": "fremtpl2_severity", "source_rows": len(severity), "demo_rows": len(severity_sample)}
    )

    predictions = pd.read_parquet(source / "frequency_predictions.parquet").sort_values("predicted_frequency")
    predictions["risk_decile"] = pd.qcut(
        predictions["predicted_frequency"].rank(method="first"), 10, labels=False
    )
    compact_predictions = predictions.groupby("risk_decile", as_index=False).agg(
        Exposure=("Exposure", "sum"),
        ClaimNb=("ClaimNb", "sum"),
        predicted_claim_count=("predicted_claim_count", "sum"),
        predicted_frequency=("predicted_frequency", "mean"),
    )
    compact_predictions.to_parquet(output / "frequency_predictions.parquet", index=False)
    summaries.append(
        {
            "table": "frequency_predictions",
            "source_rows": len(predictions),
            "demo_rows": len(compact_predictions),
        }
    )

    for name in (
        "frequency_calibration.parquet",
        "frequency_coefficients.parquet",
        "severity_calibration.parquet",
        "severity_coefficients.parquet",
    ):
        shutil.copy2(source / name, output / name)
    for name in ("frequency_model_metrics.json", "severity_model_metrics.json", "ingestion_audit.json"):
        shutil.copy2(source / name, output / name)
    return summaries


def main() -> None:
    settings.demo_root.mkdir(parents=True, exist_ok=True)
    summaries = _build_apra() + _build_french()
    manifest = {
        "purpose": "Compact derived artifacts for the public Streamlit demonstration.",
        "source_data": [
            "APRA National Claims and Policies Database masked aggregate reports, December 2024",
            "freMTPL2 public motor insurance dataset",
        ],
        "notes": [
            "Raw source archives and full processed datasets are intentionally excluded from Git.",
            "APRA demo tables preserve additive measures at a reduced analytical grain.",
            "French overview distributions use deterministic samples; verified totals come from the ingestion audit.",
        ],
        "tables": summaries,
    }
    _write_json(settings.demo_root / "manifest.json", manifest)
    print(f"Wrote {len(summaries)} demo artifacts to {settings.demo_root}")


if __name__ == "__main__":
    main()
