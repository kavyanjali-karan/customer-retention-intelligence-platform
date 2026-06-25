SELECT

date_key,

SUM(revenue) revenue,

SUM(visitors) visitors,

SUM(signups) signups,

SUM(activated_users) activated,

SUM(trial_users) trials,

SUM(paid_customers) paid_customers,

SUM(churned_customers) churned_customers

FROM fact_customer_retention

GROUP BY date_key;