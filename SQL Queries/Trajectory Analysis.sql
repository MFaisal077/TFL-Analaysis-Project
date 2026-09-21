SELECT 
  lchbyline.line,
  CASE 
    WHEN esc_avl.esc_avail > 95 THEN 'High' 
    WHEN esc_avl.esc_avail BETWEEN 90 AND 95 THEN 'Medium' 
    ELSE 'Low' 
  END as escalator_availability,
  ROUND(AVG(lchbyline.lost_customer_hours), 0) as avg_LCH,
  COUNT(*) as num_data_points
FROM esc_avl 
INNER JOIN lchbyline ON esc_avl.line = lchbyline.line
GROUP BY lchbyline.line, escalator_availability
ORDER BY lchbyline.line, escalator_availability DESC;