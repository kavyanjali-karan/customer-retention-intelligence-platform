SELECT

r.region_name,

SUM(f.revenue) revenue,

SUM(f.churned_customers) churned,

SUM(f.revenue)*

(

SUM(f.churned_customers)*1.0/

NULLIF(SUM(f.paid_customers),0)

)

revenue_at_risk

FROM fact_customer_retention f

JOIN dim_region r

ON f.region_key=r.region_key

GROUP BY r.region_name;