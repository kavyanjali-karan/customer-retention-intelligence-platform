SELECT

d.full_date,

SUM(f.revenue) revenue,

SUM(f.paid_customers) paid_customers,

SUM(f.churned_customers) churned,

SUM(f.visitors) visitors,

SUM(f.signups) signups

FROM fact_customer_retention f

JOIN dim_date d

ON f.date_key=d.date_key

GROUP BY d.full_date

ORDER BY d.full_date;