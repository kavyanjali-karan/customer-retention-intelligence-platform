SELECT

SUM(visitors) visitors,

SUM(signups) signups,

SUM(activated_users) activated,

SUM(trial_users) trials,

SUM(paid_customers) paid,

ROUND(

SUM(signups)*1.0/

NULLIF(SUM(visitors),0),

4

) signup_rate

FROM fact_customer_retention;