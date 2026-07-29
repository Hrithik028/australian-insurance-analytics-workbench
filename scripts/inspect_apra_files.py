"""Inspect all APRA workbooks and write a schema profile."""

from pprint import pprint

from src.apra.ingestion import inspect_sources

if __name__ == "__main__":
    report = inspect_sources()
    pprint(
        {
            "workbooks": report["workbook_count"],
            "worksheets": report["worksheet_count"],
            "overlap": report["overlap_assessment"],
        }
    )
