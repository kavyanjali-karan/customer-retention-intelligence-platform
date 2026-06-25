SELECT

CURRENT_DATE refresh_date,

COUNT(*) rows_loaded,

COUNT(DISTINCT customer_key) customers_loaded,

SUM(revenue) revenue_loaded

FROM fact_customer_retention;