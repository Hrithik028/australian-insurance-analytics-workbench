SELECT state_jurisdiction,
       SUM(number_of_claims_reported1) AS claims_reported,
       SUM(gross_claims_incurred) AS incurred,
       SUM(gross_claims_incurred) / NULLIF(SUM(number_of_claims_reported1), 0) AS severity,
       RANK() OVER (
           ORDER BY SUM(gross_claims_incurred) / NULLIF(SUM(number_of_claims_reported1), 0) DESC
       ) AS severity_rank
FROM claims_by_state_loi
GROUP BY state_jurisdiction;

