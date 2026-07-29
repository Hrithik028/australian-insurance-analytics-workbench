SELECT
    source_file,
    COUNT(*) AS rows,
    COUNT(*) FILTER (WHERE is_negative_payment) AS negative_payments,
    COUNT(*) FILTER (WHERE is_negative_incurred) AS negative_incurred,
    COUNT(*) FILTER (WHERE is_year_sequence_anomaly) AS year_anomalies,
    COUNT(*) FILTER (WHERE is_potential_duplicate) AS potential_duplicates,
    COUNT(*) FILTER (WHERE is_schema_exception) AS schema_exceptions
FROM claims_by_state_loi
GROUP BY source_file;

