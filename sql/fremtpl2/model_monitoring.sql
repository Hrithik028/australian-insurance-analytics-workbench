WITH deciles AS (
    SELECT *,
           NTILE(10) OVER (ORDER BY predicted_frequency) AS decile
    FROM frequency_predictions
)
SELECT decile,
       COUNT(*) AS policies,
       SUM(exposure) AS exposure,
       SUM(claimnb) AS observed_claims,
       SUM(predicted_claim_count) AS expected_claims,
       SUM(claimnb) / NULLIF(SUM(predicted_claim_count), 0) AS observed_expected_ratio,
       SUM(SUM(claimnb)) OVER (ORDER BY decile) AS cumulative_claims
FROM deciles
GROUP BY decile
ORDER BY decile;

