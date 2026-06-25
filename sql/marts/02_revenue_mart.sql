SELECT

region_key,

product_key,

SUM(revenue) revenue,

SUM(paid_customers) customers

FROM fact_customer_retention

GROUP BY

region_key,

product_key;