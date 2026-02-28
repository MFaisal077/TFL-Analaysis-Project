



CREATE or Replace VIEW v_perfomance_base AS 
SELECT 
    l.line, 
    l.year,
    l.lost_customer_hours,
    e.ejt,
	c.customer_satisfaction,
	esc.esc_avail,
	sch.schedule_operated
FROM lchbyline l 
Left JOIN excess_journey_time e 
    ON l.line = e.line 
    AND l.year = e.year
Left Join css c 
 on l.line=c.line
 and l.year=c.year
left join esc_avl esc
on l.line=esc.line and l.year=esc.year
left join schedule_operated sch
on l.line=sch.line and l.year=sch.year;