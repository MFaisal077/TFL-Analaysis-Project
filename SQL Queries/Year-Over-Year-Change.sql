SELECT 
    "year",
    line,
    lost_customer_hours,
    LAG(lost_customer_hours) OVER (PARTITION BY line ORDER BY "year") as prev_year,
    coalesce(lost_customer_hours - LAG(lost_customer_hours) OVER (PARTITION BY line ORDER BY "year"),0) as year_over_year_change
FROM lchbyline
ORDER BY line, "year";