WITH development AS (
    SELECT accident_year,
           reporting_year - accident_year AS development_period,
           SUM(gross_claim_payments) AS payments,
           SUM(gross_claims_incurred) AS incurred
    FROM claims_by_state_loi
    WHERE accident_year IS NOT NULL
      AND reporting_year >= accident_year
    GROUP BY ALL
)
SELECT *,
       SUM(payments) OVER (
           PARTITION BY accident_year ORDER BY development_period
       ) AS cumulative_payments,
       SUM(incurred) OVER (
           PARTITION BY accident_year ORDER BY development_period
       ) AS cumulative_incurred
FROM development;

