"""freMTPL2 ingestion, join validation, and Parquet outputs."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from src.config import Settings, settings
from src.fremtpl2.download import acquire_fremtpl2
from src.fremtpl2.validation import validate_frequency, validate_severity


def build_fremtpl2_dataset(config: Settings = settings) -> dict[str, object]:
    if not config.enable_french_module:
        return {"enabled": False, "reason": "ENABLE_FRENCH_MODULE=false"}
    metadata = acquire_fremtpl2(config)
    frequency = pd.read_csv(config.french_external / "freMTPL2freq.csv")
    severity = pd.read_csv(config.french_external / "freMTPL2sev.csv")
    validate_frequency(frequency)
    validate_severity(severity)
    severity_positive = severity.loc[severity["ClaimAmount"].gt(0)].copy()
    severity_features = severity_positive.merge(
        frequency, on="IDpol", how="left", validate="many_to_one", indicator=True
    )
    unmatched = int(severity_features["_merge"].ne("both").sum())
    severity_features = severity_features.loc[severity_features["_merge"].eq("both")].drop(columns="_merge")
    config.french_processed.mkdir(parents=True, exist_ok=True)
    frequency.to_parquet(config.french_processed / "fremtpl2_frequency.parquet", index=False)
    severity_positive.to_parquet(config.french_processed / "fremtpl2_severity.parquet", index=False)
    severity_features.to_parquet(config.french_processed / "fremtpl2_severity_features.parquet", index=False)
    audit = {
        "enabled": True,
        "generated_at": datetime.now(UTC).isoformat(),
        "revision": metadata["revision"],
        "frequency_rows": len(frequency),
        "severity_rows": len(severity),
        "positive_severity_rows": len(severity_positive),
        "matched_severity_rows": len(severity_features),
        "unmatched_severity_rows": unmatched,
        "total_exposure": float(frequency["Exposure"].sum()),
        "total_claims": int(frequency["ClaimNb"].sum()),
    }
    (config.french_processed / "ingestion_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit
