"""Build curated APRA Parquet tables and DuckDB tables."""

from pprint import pprint

from src.apra.ingestion import build_apra_dataset
from src.database.schema import build_database

if __name__ == "__main__":
    result = build_apra_dataset()
    pprint({"ingested": result["tables"], "duckdb_tables": build_database()})
