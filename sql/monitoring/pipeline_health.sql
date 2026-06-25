SELECT

CURRENT_TIMESTAMP refresh_timestamp,

COUNT(*) rows_loaded,

SUM(revenue) revenue_loaded

FROM fact_customer_retention;