WITH mix AS (
    SELECT reporting_year, class_of_business,
           SUM(risk_in_force_weighted) AS exposure,
           SUM(gross_earned_premium) AS earned_premium
    FROM policies_by_state_loi
    GROUP BY ALL
)
SELECT *,
       exposure / NULLIF(SUM(exposure) OVER (PARTITION BY reporting_year), 0) AS exposure_mix,
       AVG(exposure) OVER (
           PARTITION BY class_of_business ORDER BY reporting_year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) AS exposure_3y_average
FROM mix;

