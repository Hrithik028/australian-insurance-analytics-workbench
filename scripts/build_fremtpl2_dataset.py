"""Build validated freMTPL2 Parquet tables."""

from pprint import pprint

from src.database.schema import build_database
from src.fremtpl2.ingestion import build_fremtpl2_dataset

if __name__ == "__main__":
    pprint(build_fremtpl2_dataset())
    pprint({"duckdb_tables": build_database()})
