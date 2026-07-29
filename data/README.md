# Data handling

This directory follows a raw → interim → processed pattern.

- `raw/apra/` contains the two local APRA ZIP archives.
- `external/fremtpl2/` contains the revision-pinned Hugging Face cache and checksum metadata.
- `interim/apra/` contains safely extracted workbooks and raw-value Parquet snapshots.
- `processed/apra/` contains one curated Parquet table and exception file per workbook.
- `processed/fremtpl2/` contains validated source tables, joined severity features, model outputs and
  calibration artifacts.

All data layers are ignored by Git. No source file is redistributed by this repository. Missing
values remain missing, negative financial values remain present, and no synthetic data is silently
substituted for an unavailable source.

