SELECT
    vehbrand,
    COUNT(*) AS positive_claims,
    AVG(claimamount) AS average_severity,
    MEDIAN(claimamount) AS median_severity,
    QUANTILE_CONT(claimamount, 0.99) AS p99_severity
FROM fremtpl2_severity_features
GROUP BY vehbrand
ORDER BY average_severity DESC;

