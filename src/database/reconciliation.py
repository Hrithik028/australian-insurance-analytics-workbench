"""Source, Parquet, and DuckDB row-count reconciliation."""

from __future__ import annotations

import json

import pandas as pd

from src.config import Settings, settings
from src.database.connection import connect


def reconcile(config: Settings = settings) -> pd.DataFrame:
    audit_path = config.apra_processed / "ingestion_audit.json"
    if not audit_path.exists():
        raise FileNotFoundError("Run the APRA build before reconciliation")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))["tables"]
    connection = connect(read_only=True)
    rows = []
    try:
        for record in audit:
            table = record["table"]
            parquet_rows = len(pd.read_parquet(record["output"], columns=["source_file"]))
            database_rows = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            rows.append(
                {
                    "table": table,
                    "source_rows": record["source_rows"],
                    "parquet_rows": parquet_rows,
                    "duckdb_rows": database_rows,
                    "reconciled": record["source_rows"] == parquet_rows == database_rows,
                }
            )
    finally:
        connection.close()
    return pd.DataFrame(rows)
