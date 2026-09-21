CREATE OR REPLACE VIEW v_lch_category_contribution AS
WITH yearly_total AS (
    SELECT
        "year",
        SUM(lost_customer_hours) AS total_lch
    FROM lchbycategory
    GROUP BY "year"
)
SELECT
    c."year",
    c.category,
    c.lost_customer_hours,
    ROUND(
        (c.lost_customer_hours::numeric / NULLIF(t.total_lch, 0)) * 100,
        2
    ) AS percent_contribution
FROM lchbycategory c
JOIN yearly_total t
    ON c."year" = t."year"
ORDER BY c."year", percent_contribution DESC;