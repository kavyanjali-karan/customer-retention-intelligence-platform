SELECT

COUNT(*) total_rows,

COUNT(DISTINCT customer_key) unique_customers,

SUM(

CASE

WHEN revenue<0

THEN 1

ELSE 0

END

)

invalid_revenue

FROM fact_customer_retention;