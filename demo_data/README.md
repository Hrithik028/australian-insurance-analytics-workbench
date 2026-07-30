# Public demo data

This directory contains compact, derived artifacts used by the hosted Streamlit application.
The raw APRA archives and full freMTPL2 files are public, but they are intentionally not copied
into Git.

- APRA demo tables aggregate the verified curated outputs to the dimensions required by the app.
- French distributions use deterministic samples; model calibration and coefficient tables are
  the verified generated outputs.
- Full project totals shown in the app come from the sanitized ingestion audits.
- `manifest.json` records the source and demo row counts for every reduced artifact.

Rebuild these files after running the full pipelines:

```bash
python scripts/build_demo_data.py
```
