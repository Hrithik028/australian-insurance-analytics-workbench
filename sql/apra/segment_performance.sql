WITH segments AS (
    SELECT class_of_business,
           SUM(number_of_claims_reported1) AS claims,
           SUM(number_of_claims_finalised) AS finalised,
           SUM(gross_claims_incurred) AS incurred
    FROM claims_by_state_loi
    GROUP BY class_of_business
)
SELECT *,
       incurred / NULLIF(claims, 0) AS severity,
       finalised / NULLIF(claims, 0) AS finalisation_ratio,
       incurred / NULLIF(SUM(incurred) OVER (), 0) AS incurred_share
FROM segments;

