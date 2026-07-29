"""Load processed Parquet datasets into DuckDB."""

from __future__ import annotations

from pathlib import Path

from src.config import Settings, settings
from src.database.connection import connect


def load_parquet_directory(directory: Path, prefix: str = "") -> list[str]:
    tables: list[str] = []
    connection = connect()
    try:
        for path in sorted(directory.glob("*.parquet")):
            if path.stem.endswith("_exceptions"):
                continue
            name = f"{prefix}{path.stem}"
            escaped = str(path).replace("'", "''")
            connection.execute(f"CREATE OR REPLACE TABLE \"{name}\" AS SELECT * FROM read_parquet('{escaped}')")
            tables.append(name)
    finally:
        connection.close()
    return tables


def build_database(config: Settings = settings) -> list[str]:
    tables = load_parquet_directory(config.apra_processed)
    if config.enable_french_module and config.french_processed.exists():
        tables.extend(load_parquet_directory(config.french_processed))
    return tables
