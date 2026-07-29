# Methodology

## APRA

Every workbook is inspected before ingestion. Column names are standardised while original labels
remain in metadata. Negative financial values and missing values are preserved and flagged.
Alternate state, occupation, excess and indemnity-limit reports are overlapping marginal cuts,
so analytics select exactly one report table at a time. Claims development is descriptive and
does not constitute a production reserve estimate.

## freMTPL2

The frequency baseline is a Poisson GLM with `log(exposure)` as an offset. A Negative Binomial GLM
is fitted when Pearson dispersion is materially above 1.5. The severity baseline is a Gamma GLM
with log link on strictly positive claim amounts. Policy ID is excluded from model features and
the train/test split is policy-disjoint.

Estimated technical claims cost equals expected claim frequency multiplied by expected claim
severity. Loading simulations are transparent and are not final customer premiums.

