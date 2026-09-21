CREATE OR REPLACE VIEW v_data_quality_report AS
SELECT
    line,
    COUNT(*) AS years_total,

    COUNT(ejt) AS years_with_ejt,
    COUNT(customer_satisfaction) AS years_with_css,
    COUNT(schedule_operated) AS years_with_schedule,
    COUNT(esc_avail) AS years_with_esc,

    COUNT(*) - COUNT(ejt) AS missing_ejt_years,
    COUNT(*) - COUNT(customer_satisfaction) AS missing_css_years,
    COUNT(*) - COUNT(schedule_operated) AS missing_schedule_years,
    COUNT(*) - COUNT(esc_avail) AS missing_esc_years,

    SUM(CASE WHEN esc_avail = 0 THEN 1 ELSE 0 END) AS esc_zero_years
FROM v_perfomance_base
GROUP BY line
ORDER BY missing_ejt_years DESC, missing_css_years DESC;