SELECT
    region,
    SUM(exposure) AS exposure,
    SUM(claimnb) AS claims,
    SUM(claimnb) / NULLIF(SUM(exposure), 0) AS observed_frequency
FROM fremtpl2_frequency
GROUP BY region
ORDER BY observed_frequency DESC;

