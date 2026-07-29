# Data dictionary

The generated inspection profile is written to
`data/processed/apra/inspection_report.json`. APRA fields observed in the December 2024 masked
reports include:

| Field | Meaning | Availability |
|---|---|---|
| `reporting_year` | APRA reporting year | Policy and claims reports |
| `accident_year` | Claim accident year | Claims reports |
| `reported_year` | Claim reporting year | Claims reports |
| `finalised_year` | Claim finalisation year | Claims reports |
| `risk_in_force_weighted` | Weighted risk-in-force exposure | Policy reports |
| `gross_earned_premium` | Gross earned premium | Policy reports |
| `number_of_claims_reported1` | Reported claim count | Claims reports |
| `number_of_claims_finalised` | Finalised claim count | Claims reports |
| `gross_claim_payments` | Gross claim payment movement | Claims reports |
| `gross_claims_incurred` | Gross incurred claim movement | Claims reports |

`number_of_risks_written1` and `gross_written_premium_1` are retained but are not used when absent.
Source file, source sheet, report type, report dimension and ingestion timestamp are added to every
curated table.

