-- One report basis only: never UNION ALL alternate APRA cuts.
WITH yearly AS (
    SELECT
        reporting_year,
        SUM(risk_in_force_weighted) AS exposure,
        SUM(gross_earned_premium) AS earned_premium
    FROM policies_by_state_loi
    GROUP BY reporting_year
)
SELECT
    *,
    earned_premium / NULLIF(exposure, 0) AS average_earned_premium,
    (exposure / NULLIF(LAG(exposure) OVER (ORDER BY reporting_year), 0)) - 1 AS exposure_yoy
FROM yearly
ORDER BY reporting_year;

