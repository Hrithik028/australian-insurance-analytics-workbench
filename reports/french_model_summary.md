# French model summary

French motor third-party liability data is used as an educational actuarial modelling dataset.
Results are not directly representative of the Australian motor-insurance market.

## Dataset profile

- 678,013 policy-frequency rows, 358,499.4 exposure and 36,102 claims.
- 26,639 positive claim rows; 26,444 matched to frequency features and 195 documented as unmatched.
- Hugging Face revision `b645a3d34da6edf421785c83ddd39637b6553a10` with SHA-256 checksums stored beside the cached files.

## Frequency

The Poisson GLM baseline showed dispersion of 2.510, so the Negative Binomial
challenger was selected. Held-out observed frequency was 0.10110 versus
0.10179 predicted. Mean Poisson deviance was
0.3210. Exposure entered as `log(Exposure)` offset.

## Severity

The Gamma log-link GLM retained all positive matched claims without capping or winsorisation.
Held-out observed mean severity was €1,953.32 versus
€2,323.09 predicted; Gamma deviance was
1.5796 and MAE was €2,080.59. The overprediction gap is a
known calibration limitation.

## Technical claims cost and governance

Technical claims cost is expected frequency multiplied by expected severity. Policy ID is excluded
from features, splits are policy-disjoint, and simulated loadings are shown separately. The result
is not a final customer premium and is not an Australian market indication.
