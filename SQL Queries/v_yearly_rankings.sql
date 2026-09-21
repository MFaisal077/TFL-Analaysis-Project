CREATE OR REPLACE VIEW v_yearly_rankings as select a.line, a."year",a.lost_customer_hours,a.schedule_operated,customer_satisfaction,esc_avail,ejt,yoy_change,DENSE_RANK() OVER (
    PARTITION BY a."year"
    ORDER BY a.lost_customer_hours ASC
) as rank_lch_best,DENSE_RANK() OVER (
    PARTITION BY a."year"
    ORDER BY a.schedule_operated DESC NULLS LAST
) as rank_schedule_best,DENSE_RANK() OVER (
    PARTITION BY a."year"
    ORDER BY a.customer_satisfaction DESC NULLS LAST
)  as rank_css_best from v_perfomance_base a left join v_analytics b on a.line=b.line and a.year=b.year;


