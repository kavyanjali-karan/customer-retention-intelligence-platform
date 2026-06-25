SELECT

customer_key,

SUM(revenue) total_revenue,

SUM(paid_customers) paid_customers,

SUM(churned_customers) churned_customers,

ROUND(

1-

SUM(churned_customers)*1.0/

NULLIF(SUM(paid_customers),0),

2

) retention_rate

FROM fact_customer_retention

GROUP BY customer_key;