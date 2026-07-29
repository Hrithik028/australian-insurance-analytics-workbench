"""Generate quality summaries and verify row-count reconciliation."""

import json

import pandas as pd

from src.apra.quality import quality_summary
from src.config import settings
from src.database.reconciliation import reconcile

if __name__ == "__main__":
    outputs = {}
    for path in settings.apra_processed.glob("*.parquet"):
        if path.stem.endswith("_exceptions"):
            continue
        summary = quality_summary(pd.read_parquet(path))
        destination = settings.apra_processed / f"{path.stem}_quality.csv"
        summary.to_csv(destination, index=False)
        outputs[path.stem] = summary.to_dict(orient="records")
    reconciliation = reconcile()
    reconciliation.to_csv(settings.apra_processed / "reconciliation.csv", index=False)
    print(json.dumps({"quality": outputs, "reconciliation": reconciliation.to_dict("records")}, indent=2))
