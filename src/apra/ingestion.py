"""Workbook inspection and auditable APRA ingestion."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.apra.cleaning import standardise_frame
from src.apra.discovery import list_worksheets, safe_extract
from src.apra.metrics import add_claim_metrics, add_policy_metrics
from src.apra.schema import CATEGORY_COLUMNS, classify_report, table_name
from src.apra.validation import add_quality_flags, exception_rows
from src.config import Settings, settings
from src.utils import unique_names


def extract_sources(config: Settings = settings) -> list[Path]:
    paths: list[Path] = []
    for archive in [config.apra_policy_zip, config.apra_claims_zip]:
        if not archive.exists():
            raise FileNotFoundError(f"Required APRA archive not found: {archive}")
        destination = config.apra_interim / archive.stem
        paths.extend(safe_extract(archive, destination))
    return sorted(paths)


def inspect_workbook(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for sheet in list_worksheets(path):
        frame = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
        cleaned, mapping = standardise_frame(frame)
        years: dict[str, dict[str, int | None]] = {}
        for column in [name for name in cleaned if name.endswith("_year")]:
            valid = cleaned[column].dropna()
            years[column] = {
                "minimum": int(valid.min()) if not valid.empty else None,
                "maximum": int(valid.max()) if not valid.empty else None,
            }
        categories = {
            column: sorted(map(str, cleaned[column].dropna().unique()))[:250]
            for column in CATEGORY_COLUMNS
            if column in cleaned
        }
        records.append(
            {
                "workbook": path.name,
                "worksheet": sheet,
                "rows": int(len(cleaned)),
                "columns": int(len(cleaned.columns)),
                "column_mapping": mapping,
                "dtypes": {column: str(dtype) for column, dtype in cleaned.dtypes.items()},
                "year_ranges": years,
                "missing_rates": {column: round(float(cleaned[column].isna().mean()), 6) for column in cleaned},
                "categories": categories,
            }
        )
    return records


def inspect_sources(config: Settings = settings) -> dict[str, object]:
    workbooks = extract_sources(config)
    sheets = [item for path in workbooks for item in inspect_workbook(path)]
    output = {
        "generated_at": datetime.now(UTC).isoformat(),
        "archives": [str(config.apra_policy_zip), str(config.apra_claims_zip)],
        "workbook_count": len(workbooks),
        "worksheet_count": len(sheets),
        "worksheets": sheets,
        "overlap_assessment": {
            "status": "material_overlap_confirmed",
            "rule": (
                "State/occupation and LOI/EDA workbooks are alternate marginal cuts "
                "of the same portfolio. Never sum totals across workbooks."
            ),
            "safe_use": (
                "Select one report table as an analytical basis; use the other tables "
                "for alternate segment views and reconciliation comparisons."
            ),
        },
    }
    config.apra_processed.mkdir(parents=True, exist_ok=True)
    path = config.apra_processed / "inspection_report.json"
    path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    return output


def _read_sheet(path: Path, sheet: str) -> tuple[pd.DataFrame, dict[str, str], pd.DataFrame]:
    raw = pd.read_excel(path, sheet_name=sheet, engine="openpyxl", dtype=object)
    raw_snapshot = raw.copy()
    raw_snapshot.columns = unique_names(list(raw_snapshot.columns))
    raw_snapshot = raw_snapshot.loc[:, ~raw_snapshot.columns.str.startswith("unnamed")]
    raw_snapshot = raw_snapshot.astype("string")
    cleaned, mapping = standardise_frame(raw)
    return cleaned, mapping, raw_snapshot


def build_apra_dataset(config: Settings = settings) -> dict[str, object]:
    workbooks = extract_sources(config)
    config.apra_processed.mkdir(parents=True, exist_ok=True)
    config.apra_interim.mkdir(parents=True, exist_ok=True)
    audit: list[dict[str, object]] = []
    metadata: dict[str, object] = {}
    for workbook in workbooks:
        for sheet in list_worksheets(workbook):
            frame, mapping, raw_snapshot = _read_sheet(workbook, sheet)
            report_type, geography, band = classify_report(workbook.name)
            name = table_name(workbook.name)
            raw_snapshot.to_parquet(config.apra_interim / f"{name}_raw.parquet", index=False)
            frame["source_file"] = workbook.name
            frame["source_sheet"] = sheet
            frame["source_report_type"] = report_type
            frame["source_dimension"] = f"{geography}_{band}"
            frame["ingested_at"] = datetime.now(UTC)
            frame = add_quality_flags(frame)
            frame = add_claim_metrics(frame) if report_type == "claims" else add_policy_metrics(frame)
            output = config.apra_processed / f"{name}.parquet"
            frame.to_parquet(output, index=False)
            exceptions = exception_rows(frame)
            exception_path = config.apra_processed / f"{name}_exceptions.parquet"
            exceptions.to_parquet(exception_path, index=False)
            audit.append(
                {
                    "table": name,
                    "source_file": workbook.name,
                    "source_sheet": sheet,
                    "source_rows": len(frame),
                    "processed_rows": len(frame),
                    "exception_rows": len(exceptions),
                    "output": str(output),
                }
            )
            metadata[name] = {"original_columns": mapping}
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "tables": audit,
        "metadata": metadata,
        "overlap_rule": "Never add totals across APRA report tables.",
    }
    (config.apra_processed / "ingestion_audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
