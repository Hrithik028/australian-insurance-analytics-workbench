WITH ranked AS (
    SELECT *,
           NTILE(10) OVER (ORDER BY predicted_frequency) AS risk_decile
    FROM frequency_predictions
)
SELECT risk_decile,
       SUM(exposure) AS exposure,
       SUM(claimnb) / NULLIF(SUM(exposure), 0) AS observed_frequency,
       SUM(predicted_claim_count) / NULLIF(SUM(exposure), 0) AS predicted_frequency
FROM ranked
GROUP BY risk_decile
ORDER BY risk_decile;

