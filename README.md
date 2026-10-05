# Customer Retention Intelligence Platform

[![CI](https://github.com/kavyanjali-karan/customer-retention-intelligence-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/kavyanjali-karan/customer-retention-intelligence-platform/actions/workflows/ci.yml) [![tests: 10 passed](https://img.shields.io/badge/tests-10%20passed-2ea44f)](tests/) [![license: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Every Monday, the customer success team in this story faced the same
dilemma: a high-value Enterprise account had gone quiet, a cluster of SMB
customers was quietly shrinking their annual spend, and there was time
and budget for exactly one save play. No data existed to say which one to
pick.

This platform is built for that decision. It scores all 15,000 customers
of a **simulated** SaaS business for churn risk from their activity and
revenue history, maps each segment to a specific retention playbook, and
projects 8–12% lifetime value lift on the highest-risk SMB cohort
($554K–$831K annualized). The
[interactive dashboard](https://kavyanjali-karan.github.io/customer-retention-intelligence-platform/dashboard.html)
regenerates whenever the repo changes, so the live page and the
screenshots below never disagree.

## Why churn was invisible

Churn showed up in the aggregate numbers, but never early enough to act
on. Nobody could answer "which accounts do we save first?", so retention
campaigns went out uniformly regardless of risk, and high-value
Enterprise accounts churned at the same rate as SMBs. Across a year, that
is roughly $54M of revenue walking out the door with no intervention
process attached to it.

## What the system does

1. **Scores all 15,000 customers** for churn probability. A FastAPI
   service turns activity signals (login frequency, feature usage,
   support tickets) plus revenue history into a per-customer risk score
2. **Maps each risk tier to a playbook**, written separately for SMB,
   Mid-Market and Enterprise segments
3. **Puts a number on exposure**: $54.27M in churn revenue and $54.26M in
   contraction (coincidentally close this year), broken down per customer
   so outreach can be prioritized
4. **Sizes the prize**: the top 50 highest-risk SMB accounts hold $611K
   in ARR and $577K revenue at risk; an 8–12% LTV improvement on that
   cohort is worth $554K–$831K in annualized recovered revenue
5. **Puts it in front of the business**: Power BI reports for customer
   health scores, cohort retention and revenue-at-risk, with DAX measures
   for monitoring

## Metrics

Key metrics tracked across the platform:

| Metric | Value | Source |
|--------|-------|--------|
| Total Customers | 15,000 | `customers.csv` |
| Active Customers | 13,528 (90.2%) | Status field |
| Inactive Customers | 1,472 (9.8%) | Status field |
| Total Revenue | $539.9M | Revenue transactions |
| Churn Revenue | $54.27M (10.1%) | Revenue type breakdown |
| Contraction Revenue | $54.26M (10.1%) | Revenue type breakdown |
| Expansion Revenue | $108.6M (20.1%) | Revenue type breakdown |
| Revenue Transactions | 120,000 | Transaction records |
| Activity Records | 182,750 | Login/usage events |

## Data

Simulated SaaS/subscription business with 15,000 customers across 3 segments and 8 industries:

| Dataset | Records | Description |
|---------|---------|-------------|
| `customers.csv` | 15,000 | Customer profiles — segment, industry, region, contract value ($3K–$250K) |
| `revenue_transactions.csv` | 120,000 | Monthly revenue per customer — Renewal, Expansion, New, Churn, Contraction |
| `customer_activity.csv` | 182,750 | Login events, feature usage, support tickets |

### Segment Breakdown

| Segment | Customers | Share |
|---------|-----------|-------|
| SMB | 6,788 | 45.3% |
| Mid-Market | 5,237 | 34.9% |
| Enterprise | 2,975 | 19.8% |

### Revenue by Type

| Type | Amount | Share |
|------|--------|-------|
| Renewal | $215.5M | 39.9% |
| Expansion | $108.6M | 20.1% |
| New | $107.3M | 19.9% |
| Churn | $54.27M | 10.1% |
| Contraction | $54.26M | 10.1% |

To rebuild the datasets from scratch:
```bash
pip install pandas numpy
python data/generate_data.py
```

## Outputs

The `outputs/` folder contains actionable deliverables:

| File | Description |
|------|-------------|
| `retention_recommendations.csv` | 50 at-risk SMB customers with churn probability, revenue at risk, and prioritized actions |
| `ltv_impact_summary.csv` | Top 50 highest-risk SMB customers (>65% churn probability) hold $611K in ARR and $577K revenue at risk; 8–12% LTV lift = $554K–$831K annualized |
| `churn_risk_export.csv` | Full churn risk scores for all 15,000 customers |
| `customer_health_export.csv` | Health scores combining activity, revenue, and support signals |
| `revenue_at_risk_export.csv` | Per-customer revenue exposure for prioritized outreach |
| `executive_business_review.csv` | Monthly executive rollup for business reviews |
| `quarterly_business_review.csv` | Quarterly aggregation with trend analysis |

## Dashboards

I didn't draw a single chart here. Both renderers read this repo's
curated data: [`python/generate_dashboard_pngs.py`](python/generate_dashboard_pngs.py)
for the stills and [`python/generate_dashboards.py`](python/generate_dashboards.py)
for the interactive page, all on one shared visual language:

- **Executive Overview** — KPI cards, revenue trend, churn risk distribution
- **Customer Health** — Individual health scores, activity trends, risk flags
- **Cohort Analysis** — Retention curves by signup cohort and segment
- **Revenue at Risk** — Top accounts by revenue exposure, intervention priority
- **Churn Analysis** — Churn-flagged accounts ranked by risk driver

### Executive Overview
![Executive Overview](assets/executive_overview.png)

### Customer Health
![Customer Health](assets/customer_health.png)

### Cohort Analysis
![Cohort Analysis](assets/cohort_analysis.png)

### Revenue at Risk
![Revenue at Risk](assets/revenue_at_risk.png)

### Churn Analysis
![Churn Analysis](assets/churn_analysis.png)

### Regenerating the dashboards

```bash
python data/generate_data.py              # datasets (seeded, reproducible)
python python/generate_dashboard_pngs.py  # renders assets/*.png
python python/generate_dashboards.py      # builds assets/dashboard.html (Chart.js inlined, no CDN)
```

The Pages workflow reruns both renderers against the committed data
before it publishes, which is why the live view and these screenshots
can't drift apart.

## Project Structure

```
├── data/
│   ├── raw/              # customers, revenue_transactions, customer_activity
│   ├── curated/          # Dimension tables, fact tables
│   └── warehouse/        # Metric definitions, targets
├── sql/
│   ├── ddl/              # Table definitions
│   ├── staging/          # Staging views
│   ├── marts/            # Business marts
│   ├── metrics/          # Metric calculations
│   ├── monitoring/       # Data quality checks
│   └── reporting/        # Dashboard queries
├── python/
│   ├── extraction/       # Data loading
│   ├── transformation/   # Cleaning and enrichment
│   ├── validation/       # Quality checks
│   ├── monitoring/       # Pipeline health
│   ├── reporting/        # Business review and export scripts
│   ├── generate_dashboard_pngs.py   # Renders the dashboard PNGs in assets/
│   └── generate_dashboards.py       # Builds the interactive assets/dashboard.html
├── api/                  # FastAPI churn scoring service
├── powerbi/
│   ├── dax/              # DAX measure library
│   └── model/            # Semantic model docs
├── outputs/              # Retention recommendations, LTV impact, risk exports
├── docs/                 # Architecture, glossary, metric dictionary, scorecard
├── tests/                # Data quality tests (pytest)
└── assets/               # Dashboard screenshots
```

## Running Tests

```bash
pip install pytest pandas numpy
pytest
```

10 tests covering data quality, revenue-type reconciliation, and churn-score inputs. The data builds itself on first run, so a fresh clone passes with no setup.

## Tech Stack

SQL, Python (pandas, numpy), FastAPI, Power BI, DAX, Docker, GitHub Actions, pytest, Git
