SELECT 
    esc_avl.line,
    CASE 
        WHEN esc_avl.esc_avail > 95 THEN 'High'
        WHEN esc_avl.esc_avail BETWEEN 90 AND 95 THEN 'Medium'
        ELSE 'Low'
    END as esc_tier,
    ROUND(AVG(css.customer_satisfaction), 1) as avg_satisfaction,
    COUNT(*) as num_years
FROM css 
INNER JOIN esc_avl ON css.line = esc_avl.line AND css."year" = esc_avl."year"
GROUP BY esc_avl.line, esc_tier
ORDER BY esc_avl.line, esc_tier DESC;