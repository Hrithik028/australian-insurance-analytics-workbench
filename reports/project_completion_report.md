# Project completion report

## Data processed

- `Claim_by_OCC_EDA_Masked.xlsx`: 158,407 rows
- `Claim_by_OCC_LOI_Masked.xlsx`: 146,439 rows
- `Claim_by_State_EDA_Masked.xlsx`: 122,739 rows
- `Claim_by_state_LOI_Masked.xlsx`: 118,852 rows
- `Policy_by_OCC_EDA_Masked.xlsx`: 60,772 rows
- `Policy_by_OCC_LOI_Masked.xlsx`: 66,453 rows
- `Policy_by_State_EDA_Masked.xlsx`: 21,940 rows
- `Policy_by_State_LOI_Masked.xlsx`: 24,428 rows
- `freMTPL2freq.csv`: 678,013 rows
- `freMTPL2sev.csv`: 26,639 rows

## Outputs

- DuckDB curated tables: 17
- Streamlit pages: 15
- Frequency model: Negative Binomial GLM
- Severity model: Gamma GLM with log link
- APRA row reconciliation: 8/8 tables passed
- Tests: 20 passed
- Ruff: all checks passed; 88 files formatted
- Streamlit smoke check: 15/15 pages passed; live health endpoint returned HTTP 200; disabled mode passed
- Mermaid sources: 3
- SVG diagrams: 3

## Known limitations

APRA reports are overlapping aggregate cuts; French results are educational and not representative
of Australia; 195 positive severity records lack a matching frequency policy; and the held-out
severity model overpredicts mean severity.
