"""DuckDB connection management."""

from __future__ import annotations

from pathlib import Path

import duckdb

from src.config import settings


def connect(path: Path | None = None, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    target = path or settings.duckdb_path
    target.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(target), read_only=read_only)
