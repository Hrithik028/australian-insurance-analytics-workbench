"""Create concise, reproducible notebook entry points."""

from pathlib import Path

import nbformat as nbf

from src.config import settings

NOTEBOOKS = [
    (
        "01_apra_data_profiling.ipynb",
        "APRA data profiling",
        "from src.apra.ingestion import inspect_sources\ninspect_sources()",
    ),
    (
        "02_apra_data_cleaning.ipynb",
        "APRA data cleaning",
        "from src.apra.ingestion import build_apra_dataset\nbuild_apra_dataset()",
    ),
    (
        "03_apra_portfolio_analysis.ipynb",
        "APRA portfolio analysis",
        "import pandas as pd\npd.read_parquet('../data/processed/apra/policies_by_state_loi.parquet').head()",
    ),
    (
        "04_apra_claims_development.ipynb",
        "APRA claims development",
        "from src.apra.development import development_matrix",
    ),
    ("05_fremtpl2_profiling.ipynb", "freMTPL2 profiling", "from src.fremtpl2.ingestion import build_fremtpl2_dataset"),
    ("06_frequency_modelling.ipynb", "Frequency modelling", "from src.fremtpl2.frequency import train_frequency_model"),
    ("07_severity_modelling.ipynb", "Severity modelling", "from src.fremtpl2.severity import train_severity_model"),
    (
        "08_technical_premium.ipynb",
        "Technical claims cost",
        "from src.fremtpl2.premium import calculate_loaded_premium",
    ),
]

if __name__ == "__main__":
    directory = settings.root / "notebooks"
    directory.mkdir(exist_ok=True)
    for filename, title, code in NOTEBOOKS:
        notebook = nbf.v4.new_notebook(
            cells=[
                nbf.v4.new_markdown_cell(
                    f"# {title}\n\nRun from the project environment after the documented build steps."
                ),
                nbf.v4.new_code_cell(code),
            ],
            metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        )
        nbf.write(notebook, Path(directory) / filename)
    print(f"Created {len(NOTEBOOKS)} notebooks.")
