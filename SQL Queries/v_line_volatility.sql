
create or replace view v_line_volatility as select line,STDDEV_SAMP(yoy_change),AVG(yoy_change)as avg_trend,MIN(yoy_change) as worst_drop,MAX(yoy_change) as biggest_spike,COUNT(yoy_change) as valid_years from v_analytics group by line;

