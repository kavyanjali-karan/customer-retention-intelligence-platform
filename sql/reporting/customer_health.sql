SELECT

c.customer_segment,

COUNT(DISTINCT f.customer_key) customers,

SUM(f.revenue) revenue,

SUM(f.churned_customers) churned

FROM fact_customer_retention f

JOIN dim_customer c

ON f.customer_key=c.customer_key

GROUP BY c.customer_segment;