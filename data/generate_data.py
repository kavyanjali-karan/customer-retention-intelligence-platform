import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path
from datetime import datetime

fake = Faker()
np.random.seed(42)

# =====================================================
# CONFIG
# =====================================================

N_CUSTOMERS = 15000
N_PRODUCTS = 20

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

BASE_DIR = Path(__file__).parent

RAW_DIR = BASE_DIR / "raw"
CURATED_DIR = BASE_DIR / "curated"
WAREHOUSE_DIR = BASE_DIR / "warehouse"

for directory in [RAW_DIR, CURATED_DIR, WAREHOUSE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOOKUPS
# =====================================================

SEGMENTS = [
    "Enterprise",
    "MidMarket",
    "SMB"
]

SEGMENT_PROBS = [
    0.20,
    0.35,
    0.45
]

INDUSTRIES = [
    "Technology",
    "Healthcare",
    "Retail",
    "Finance",
    "Manufacturing",
    "Education",
    "Telecom",
    "Logistics"
]

CHANNELS = [
    "Direct",
    "Partner",
    "Referral",
    "Organic",
    "Google",
    "LinkedIn",
    "Email",
    "Events"
]

REGIONS = [
    "North America",
    "Europe",
    "UK",
    "India",
    "APAC",
    "Australia",
    "Japan",
    "Middle East",
    "Africa",
    "South America",
    "Singapore",
    "Nordics"
]

PRODUCT_FAMILIES = [
    "Analytics",
    "Governance",
    "Automation",
    "Data Platform"
]

# =====================================================
# CUSTOMERS
# =====================================================

print("Generating customers...")

customer_rows = []

for i in range(1, N_CUSTOMERS + 1):

    segment = np.random.choice(
        SEGMENTS,
        p=SEGMENT_PROBS
    )

    if segment == "Enterprise":
        contract_value = np.random.randint(
            50000,
            250000
        )
    elif segment == "MidMarket":
        contract_value = np.random.randint(
            15000,
            60000
        )
    else:
        contract_value = np.random.randint(
            3000,
            15000
        )

    customer_rows.append({
        "customer_id": f"CUST{i:06}",
        "customer_name": fake.company(),
        "segment": segment,
        "industry": np.random.choice(
            INDUSTRIES
        ),
        "region_id": f"REG{np.random.randint(1,13):02}",
        "channel_id": f"CH{np.random.randint(1,9):02}",
        "signup_date": fake.date_between(
            start_date="-5y",
            end_date="-60d"
        ),
        "status": np.random.choice(
            [
                "Active",
                "Inactive"
            ],
            p=[0.90,0.10]
        ),
        "contract_value": contract_value
    })

customers_df = pd.DataFrame(
    customer_rows
)

customers_df.to_csv(
    RAW_DIR / "customers.csv",
    index=False
)

print("customers.csv generated")

# =====================================================
# PRODUCTS
# =====================================================

print("Generating products...")

product_rows = []

for i in range(1, N_PRODUCTS + 1):

    family = np.random.choice(
        PRODUCT_FAMILIES
    )

    list_price = np.random.randint(
        100,
        1500
    )

    product_rows.append({
        "product_id": f"PROD{i:03}",
        "product_family": family,
        "product_name": f"{family} Product {i}",
        "list_price": list_price
    })

products_df = pd.DataFrame(
    product_rows
)

products_df.to_csv(
    RAW_DIR / "products.csv",
    index=False
)

print("products.csv generated")

# =====================================================
# CHANNELS
# =====================================================

channel_rows = []

for idx, channel in enumerate(
    CHANNELS,
    start=1
):
    channel_rows.append({
        "channel_id": f"CH{idx:02}",
        "channel_name": channel
    })

channels_df = pd.DataFrame(
    channel_rows
)

channels_df.to_csv(
    RAW_DIR / "channels.csv",
    index=False
)

# =====================================================
# REGIONS
# =====================================================

region_rows = []

for idx, region in enumerate(
    REGIONS,
    start=1
):
    region_rows.append({
        "region_id": f"REG{idx:02}",
        "region_name": region
    })

regions_df = pd.DataFrame(
    region_rows
)

regions_df.to_csv(
    RAW_DIR / "regions.csv",
    index=False
)

print("channels.csv generated")
print("regions.csv generated")

# =====================================================
# DATE RANGE
# =====================================================

dates = pd.date_range(
    START_DATE,
    END_DATE,
    freq="D"
)

# =====================================================
# CUSTOMER ACTIVITY
# =====================================================

print("Generating customer activity...")

activity_rows = []

for current_date in dates:

    active_customers = customers_df.sample(
        250,
        replace=False
    )

    for _, customer in active_customers.iterrows():

        activity_rows.append({
            "activity_id":
                f"ACT{len(activity_rows)+1:08}",
            "activity_date":
                current_date,
            "customer_id":
                customer["customer_id"],
            "product_id":
                products_df.sample(1).iloc[0]["product_id"],
            "logins":
                np.random.randint(0,25),
            "sessions":
                np.random.randint(1,60),
            "feature_usage_score":
                round(
                    np.random.uniform(
                        0,
                        100
                    ),
                    2
                ),
            "nps_score":
                np.random.randint(
                    0,
                    11
                ),
            "active_days":
                np.random.randint(
                    1,
                    31
                )
        })

activity_df = pd.DataFrame(
    activity_rows
)

activity_df.to_csv(
    RAW_DIR /
    "customer_activity.csv",
    index=False
)

print(
    "customer_activity.csv generated"
)
# =====================================================
# SUBSCRIPTIONS
# =====================================================

print("Generating subscriptions...")

subscription_rows = []

for _, customer in customers_df.iterrows():

    start_date = fake.date_between(
        start_date="-3y",
        end_date="-180d"
    )

    renewal_date = pd.to_datetime(
        start_date
    ) + pd.DateOffset(
        months=np.random.choice(
            [12,24,36]
        )
    )

    if customer["segment"] == "Enterprise":
        mrr = np.random.randint(
            4000,
            25000
        )
    elif customer["segment"] == "MidMarket":
        mrr = np.random.randint(
            1000,
            8000
        )
    else:
        mrr = np.random.randint(
            100,
            2000
        )

    arr = mrr * 12

    subscription_rows.append({
        "subscription_id":
            f"SUB{len(subscription_rows)+1:07}",
        "customer_id":
            customer["customer_id"],
        "start_date":
            start_date,
        "renewal_date":
            renewal_date.date(),
        "subscription_status":
            np.random.choice(
                [
                    "Active",
                    "Cancelled",
                    "Pending Renewal"
                ],
                p=[
                    0.85,
                    0.05,
                    0.10
                ]
            ),
        "mrr":mrr,
        "arr":arr
    })

subscriptions_df = pd.DataFrame(
    subscription_rows
)

subscriptions_df.to_csv(
    RAW_DIR /
    "subscriptions.csv",
    index=False
)

print("subscriptions.csv generated")

# =====================================================
# SUPPORT TICKETS
# =====================================================

print("Generating support tickets...")

ticket_rows = []

for i in range(45000):

    created_date = np.random.choice(
        dates
    )

    resolved_date = pd.to_datetime(
        created_date
    ) + pd.Timedelta(
        days=np.random.randint(
            0,
            14
        )
    )

    ticket_rows.append({
        "ticket_id":
            f"TKT{i+1:08}",
        "customer_id":
            customers_df.sample(1)
            .iloc[0]["customer_id"],
        "created_date":
            created_date,
        "resolved_date":
            resolved_date,
        "priority":
            np.random.choice(
                [
                    "Low",
                    "Medium",
                    "High",
                    "Critical"
                ],
                p=[
                    0.45,
                    0.35,
                    0.15,
                    0.05
                ]
            ),
        "csat_score":
            np.random.randint(
                1,
                6
            )
    })

tickets_df = pd.DataFrame(
    ticket_rows
)

tickets_df.to_csv(
    RAW_DIR /
    "support_tickets.csv",
    index=False
)

print("support_tickets.csv generated")

# =====================================================
# REVENUE TRANSACTIONS
# =====================================================

print("Generating revenue transactions...")

revenue_rows = []

for i in range(120000):

    customer = customers_df.sample(
        1
    ).iloc[0]

    transaction_date = np.random.choice(
        dates
    )

    revenue_type = np.random.choice(
        [
            "New",
            "Renewal",
            "Expansion",
            "Contraction",
            "Churn"
        ],
        p=[
            0.20,
            0.40,
            0.20,
            0.10,
            0.10
        ]
    )

    if customer["segment"] == "Enterprise":
        amount = np.random.randint(
            1000,
            25000
        )
    elif customer["segment"] == "MidMarket":
        amount = np.random.randint(
            500,
            8000
        )
    else:
        amount = np.random.randint(
            50,
            2000
        )

    revenue_rows.append({
        "transaction_id":
            f"TRX{i+1:09}",
        "customer_id":
            customer["customer_id"],
        "transaction_date":
            transaction_date,
        "revenue_type":
            revenue_type,
        "amount":
            amount
    })

revenue_df = pd.DataFrame(
    revenue_rows
)

revenue_df.to_csv(
    RAW_DIR /
    "revenue_transactions.csv",
    index=False
)

print(
    "revenue_transactions.csv generated"
)

# =====================================================
# DIM CUSTOMER
# =====================================================

print("Creating dimensions...")

dim_customer = customers_df.copy()

dim_customer.insert(
    0,
    "customer_key",
    range(
        1,
        len(dim_customer)+1
    )
)

dim_customer.to_csv(
    CURATED_DIR /
    "dim_customer.csv",
    index=False
)

# =====================================================
# DIM PRODUCT
# =====================================================

dim_product = products_df.copy()

dim_product.insert(
    0,
    "product_key",
    range(
        1,
        len(dim_product)+1
    )
)

dim_product.to_csv(
    CURATED_DIR /
    "dim_product.csv",
    index=False
)

# =====================================================
# DIM CHANNEL
# =====================================================

dim_channel = channels_df.copy()

dim_channel.insert(
    0,
    "channel_key",
    range(
        1,
        len(dim_channel)+1
    )
)

dim_channel.to_csv(
    CURATED_DIR /
    "dim_channel.csv",
    index=False
)

# =====================================================
# DIM REGION
# =====================================================

dim_region = regions_df.copy()

dim_region.insert(
    0,
    "region_key",
    range(
        1,
        len(dim_region)+1
    )
)

dim_region.to_csv(
    CURATED_DIR /
    "dim_region.csv",
    index=False
)

# =====================================================
# DIM DATE
# =====================================================

dim_date = pd.DataFrame({
    "date":dates
})

dim_date["date_key"] = (
    dim_date["date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

dim_date["year"] = (
    dim_date["date"]
    .dt.year
)

dim_date["quarter"] = (
    dim_date["date"]
    .dt.quarter
)

dim_date["month"] = (
    dim_date["date"]
    .dt.month
)

dim_date["month_name"] = (
    dim_date["date"]
    .dt.month_name()
)

dim_date["week"] = (
    dim_date["date"]
    .dt.isocalendar()
    .week
)

dim_date.to_csv(
    CURATED_DIR /
    "dim_date.csv",
    index=False
)

print("Dimension tables generated")
# =====================================================
# LOOKUPS FOR FACT TABLES
# =====================================================

customer_lookup = dict(
    zip(
        dim_customer.customer_id,
        dim_customer.customer_key
    )
)

product_lookup = dict(
    zip(
        dim_product.product_id,
        dim_product.product_key
    )
)

region_lookup = dict(
    zip(
        dim_region.region_id,
        dim_region.region_key
    )
)

channel_lookup = dict(
    zip(
        dim_channel.channel_id,
        dim_channel.channel_key
    )
)

# =====================================================
# FACT CUSTOMER ACTIVITY
# =====================================================

print("Creating fact_customer_activity...")

activity_fact = activity_df.copy()

activity_fact["customer_key"] = (
    activity_fact["customer_id"]
    .map(customer_lookup)
)

activity_fact["product_key"] = (
    activity_fact["product_id"]
    .map(product_lookup)
)

customer_region_map = dict(
    zip(
        customers_df.customer_id,
        customers_df.region_id
    )
)

customer_channel_map = dict(
    zip(
        customers_df.customer_id,
        customers_df.channel_id
    )
)

activity_fact["region_key"] = (
    activity_fact["customer_id"]
    .map(customer_region_map)
    .map(region_lookup)
)

activity_fact["channel_key"] = (
    activity_fact["customer_id"]
    .map(customer_channel_map)
    .map(channel_lookup)
)

activity_fact["date_key"] = pd.to_datetime(
    activity_fact["activity_date"]
).dt.strftime("%Y%m%d").astype(int)

activity_fact.insert(
    0,
    "activity_key",
    range(
        1,
        len(activity_fact)+1
    )
)

activity_fact.to_csv(
    CURATED_DIR /
    "fact_customer_activity.csv",
    index=False
)

print(
    "fact_customer_activity.csv generated"
)

# =====================================================
# FACT RETENTION
# =====================================================

print("Creating fact_retention...")

retention_rows = []

for _, row in subscriptions_df.iterrows():

    retained_flag = np.random.choice(
        [1,0],
        p=[0.88,0.12]
    )

    churn_flag = 0 if retained_flag == 1 else 1

    retention_rows.append({
        "customer_id":
            row["customer_id"],
        "mrr":
            row["mrr"],
        "arr":
            row["arr"],
        "retained_flag":
            retained_flag,
        "churn_flag":
            churn_flag,
        "subscription_status":
            row["subscription_status"]
    })

retention_df = pd.DataFrame(
    retention_rows
)

retention_df["customer_key"] = (
    retention_df["customer_id"]
    .map(customer_lookup)
)

retention_df.insert(
    0,
    "retention_key",
    range(
        1,
        len(retention_df)+1
    )
)

retention_df.to_csv(
    CURATED_DIR /
    "fact_retention.csv",
    index=False
)

print(
    "fact_retention.csv generated"
)

# =====================================================
# FACT REVENUE
# =====================================================

print("Creating fact_revenue...")

fact_revenue = revenue_df.copy()

fact_revenue["customer_key"] = (
    fact_revenue["customer_id"]
    .map(customer_lookup)
)

fact_revenue["date_key"] = pd.to_datetime(
    fact_revenue["transaction_date"]
).dt.strftime("%Y%m%d").astype(int)

fact_revenue.insert(
    0,
    "revenue_key",
    range(
        1,
        len(fact_revenue)+1
    )
)

fact_revenue.to_csv(
    CURATED_DIR /
    "fact_revenue.csv",
    index=False
)

print(
    "fact_revenue.csv generated"
)

# =====================================================
# CUSTOMER HEALTH SCORES
# =====================================================

print("Creating customer_health_scores...")

health_rows = []

for _, customer in customers_df.iterrows():

    engagement_score = np.random.randint(
        20,
        100
    )

    support_score = np.random.randint(
        20,
        100
    )

    revenue_score = np.random.randint(
        20,
        100
    )

    health_score = round(
        (
            engagement_score * 0.4 +
            support_score * 0.2 +
            revenue_score * 0.4
        ),
        2
    )

    if health_score >= 80:
        band = "Healthy"
    elif health_score >= 60:
        band = "Monitor"
    elif health_score >= 40:
        band = "At Risk"
    else:
        band = "Critical"

    health_rows.append({
        "customer_id":
            customer["customer_id"],
        "health_score":
            health_score,
        "health_band":
            band,
        "engagement_score":
            engagement_score,
        "support_score":
            support_score,
        "revenue_score":
            revenue_score
    })

health_df = pd.DataFrame(
    health_rows
)

health_df.to_csv(
    CURATED_DIR /
    "customer_health_scores.csv",
    index=False
)

print(
    "customer_health_scores.csv generated"
)

# =====================================================
# CHURN PREDICTIONS
# =====================================================

print("Creating churn_predictions...")

risk_drivers = [
    "Low Usage",
    "Low NPS",
    "Support Escalations",
    "Contract Expiry",
    "Revenue Decline"
]

prediction_rows = []

for _, row in health_df.iterrows():

    churn_probability = round(
        np.random.uniform(
            0.01,
            0.95
        ),
        4
    )

    prediction_rows.append({
        "customer_id":
            row["customer_id"],
        "churn_probability":
            churn_probability,
        "predicted_churn_flag":
            1 if churn_probability > 0.65 else 0,
        "top_risk_driver":
            np.random.choice(
                risk_drivers
            )
    })

prediction_df = pd.DataFrame(
    prediction_rows
)

prediction_df.to_csv(
    CURATED_DIR /
    "churn_predictions.csv",
    index=False
)

print(
    "churn_predictions.csv generated"
)

# =====================================================
# REVENUE AT RISK
# =====================================================

print("Creating revenue_at_risk...")

subscription_lookup = subscriptions_df[
    [
        "customer_id",
        "arr"
    ]
].copy()

risk_rows = []

for _, row in prediction_df.iterrows():

    arr = subscription_lookup[
        subscription_lookup["customer_id"]
        ==
        row["customer_id"]
    ]["arr"].values[0]

    risk_pct = round(
        row["churn_probability"],
        4
    )

    risk_value = round(
        arr * risk_pct,
        2
    )

    risk_rows.append({
        "customer_id":
            row["customer_id"],
        "current_arr":
            arr,
        "risk_percentage":
            risk_pct,
        "revenue_at_risk":
            risk_value
    })

risk_df = pd.DataFrame(
    risk_rows
)

risk_df.to_csv(
    CURATED_DIR /
    "revenue_at_risk.csv",
    index=False
)

print(
    "revenue_at_risk.csv generated"
)
# =====================================================
# RETENTION COHORTS
# =====================================================

print("Creating retention_cohorts...")

cohort_rows = []

cohort_months = pd.date_range(
    START_DATE,
    END_DATE,
    freq="MS"
)

for cohort in cohort_months:

    for month_number in range(0, 26):

        retention_rate = max(
            100 - (month_number * 3.5)
            + np.random.randint(-2, 3),
            25
        )

        cohort_rows.append({
            "cohort_month":
                cohort.strftime("%Y-%m"),
            "month_number":
                month_number,
            "retention_rate":
                round(retention_rate, 2)
        })

cohort_df = pd.DataFrame(
    cohort_rows
)

cohort_df.to_csv(
    CURATED_DIR /
    "retention_cohorts.csv",
    index=False
)

print(
    "retention_cohorts.csv generated"
)

# =====================================================
# EXECUTIVE KPI TABLE
# =====================================================

print("Creating executive_kpis...")

monthly_revenue = (
    revenue_df.assign(
        month=pd.to_datetime(
            revenue_df["transaction_date"]
        ).dt.strftime("%Y-%m")
    )
    .groupby("month")["amount"]
    .sum()
    .reset_index()
)

monthly_revenue.rename(
    columns={
        "amount":"arr"
    },
    inplace=True
)

executive_rows = []

for _, row in monthly_revenue.iterrows():

    executive_rows.append({
        "month":
            row["month"],
        "customers":
            np.random.randint(
                9000,
                15000
            ),
        "retention_rate":
            round(
                np.random.uniform(
                    82,
                    96
                ),
                2
            ),
        "net_revenue_retention":
            round(
                np.random.uniform(
                    95,
                    125
                ),
                2
            ),
        "gross_revenue_retention":
            round(
                np.random.uniform(
                    80,
                    98
                ),
                2
            ),
        "arr":
            round(
                row["arr"],
                2
            ),
        "revenue_at_risk":
            round(
                np.random.uniform(
                    50000,
                    750000
                ),
                2
            )
    })

executive_df = pd.DataFrame(
    executive_rows
)

executive_df.to_csv(
    WAREHOUSE_DIR /
    "executive_kpis.csv",
    index=False
)

print(
    "executive_kpis.csv generated"
)

# =====================================================
# RETENTION TARGETS
# =====================================================

months = pd.date_range(
    START_DATE,
    END_DATE,
    freq="MS"
)

retention_targets = pd.DataFrame({
    "month":
        months.strftime("%Y-%m"),
    "retention_target":
        np.random.randint(
            88,
            96,
            len(months)
        )
})

retention_targets.to_csv(
    WAREHOUSE_DIR /
    "retention_targets.csv",
    index=False
)

print(
    "retention_targets.csv generated"
)

# =====================================================
# REVENUE TARGETS
# =====================================================

revenue_targets = pd.DataFrame({
    "month":
        months.strftime("%Y-%m"),
    "arr_target":
        np.random.randint(
            1500000,
            5000000,
            len(months)
        ),
    "nrr_target":
        np.random.randint(
            105,
            125,
            len(months)
        )
})

revenue_targets.to_csv(
    WAREHOUSE_DIR /
    "revenue_targets.csv",
    index=False
)

print(
    "revenue_targets.csv generated"
)

# =====================================================
# CUSTOMER HEALTH THRESHOLDS
# =====================================================

health_thresholds = pd.DataFrame({
    "health_band":[
        "Healthy",
        "Monitor",
        "At Risk",
        "Critical"
    ],
    "min_score":[
        80,
        60,
        40,
        0
    ],
    "max_score":[
        100,
        79,
        59,
        39
    ]
})

health_thresholds.to_csv(
    WAREHOUSE_DIR /
    "customer_health_thresholds.csv",
    index=False
)

print(
    "customer_health_thresholds.csv generated"
)

# =====================================================
# METRIC DICTIONARY
# =====================================================

metric_dictionary = pd.DataFrame({
    "metric_name":[
        "ARR",
        "MRR",
        "Retention Rate",
        "NRR",
        "GRR",
        "Revenue At Risk",
        "Customer Health",
        "Churn Probability",
        "Expansion Revenue",
        "Contraction Revenue",
        "Active Customers",
        "Support CSAT",
        "NPS",
        "Renewal Rate",
        "Product Adoption"
    ],
    "definition":[
        "Annual recurring revenue",
        "Monthly recurring revenue",
        "Customer retention percentage",
        "Net revenue retention",
        "Gross revenue retention",
        "Expected revenue loss",
        "Customer health score",
        "Predicted churn likelihood",
        "Upsell revenue",
        "Revenue contraction",
        "Active customer count",
        "Support satisfaction score",
        "Net promoter score",
        "Renewal percentage",
        "Feature usage adoption"
    ],
    "owner":"BI Team",
    "refresh_frequency":"Daily"
})

metric_dictionary.to_csv(
    WAREHOUSE_DIR /
    "metric_dictionary.csv",
    index=False
)

print(
    "metric_dictionary.csv generated"
)

# =====================================================
# BUSINESS CALENDAR
# =====================================================

calendar = pd.DataFrame({
    "event_date":[
        "2024-03-31",
        "2024-06-30",
        "2024-09-30",
        "2024-12-31",
        "2025-03-31",
        "2025-06-30",
        "2025-09-30",
        "2025-12-31",
        "2024-01-15",
        "2025-01-15"
    ],
    "event_name":[
        "Q1 Review",
        "Q2 Review",
        "Q3 Review",
        "Q4 Review",
        "Q1 Review",
        "Q2 Review",
        "Q3 Review",
        "Q4 Review",
        "Annual Planning",
        "Annual Planning"
    ],
    "event_type":[
        "QBR",
        "QBR",
        "QBR",
        "QBR",
        "QBR",
        "QBR",
        "QBR",
        "QBR",
        "Planning",
        "Planning"
    ]
})

calendar.to_csv(
    WAREHOUSE_DIR /
    "business_calendar.csv",
    index=False
)

print(
    "business_calendar.csv generated"
)

# =====================================================
# COMPLETE
# =====================================================

print("")
print("=" * 60)
print("CUSTOMER RETENTION DATASETS GENERATED SUCCESSFULLY")
print("=" * 60)
print("")

print("RAW")
print("- customers.csv")
print("- products.csv")
print("- channels.csv")
print("- regions.csv")
print("- customer_activity.csv")
print("- subscriptions.csv")
print("- support_tickets.csv")
print("- revenue_transactions.csv")

print("")
print("CURATED")
print("- dim_customer.csv")
print("- dim_product.csv")
print("- dim_channel.csv")
print("- dim_region.csv")
print("- dim_date.csv")
print("- fact_customer_activity.csv")
print("- fact_retention.csv")
print("- fact_revenue.csv")
print("- customer_health_scores.csv")
print("- churn_predictions.csv")
print("- revenue_at_risk.csv")
print("- retention_cohorts.csv")

print("")
print("WAREHOUSE")
print("- executive_kpis.csv")
print("- retention_targets.csv")
print("- revenue_targets.csv")
print("- customer_health_thresholds.csv")
print("- metric_dictionary.csv")
print("- business_calendar.csv")

print("")
print("DONE")