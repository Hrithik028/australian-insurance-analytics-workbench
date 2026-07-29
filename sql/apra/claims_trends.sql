WITH yearly AS (
    SELECT reporting_year,
           SUM(number_of_claims_reported1) AS claims_reported,
           SUM(number_of_claims_finalised) AS claims_finalised,
           SUM(gross_claim_payments) AS payments,
           SUM(gross_claims_incurred) AS incurred
    FROM claims_by_state_loi
    GROUP BY reporting_year
)
SELECT *,
       claims_finalised / NULLIF(claims_reported, 0) AS finalisation_ratio,
       incurred / NULLIF(claims_reported, 0) AS incurred_severity,
       incurred / NULLIF(LAG(incurred) OVER (ORDER BY reporting_year), 0) - 1 AS incurred_yoy
FROM yearly;

