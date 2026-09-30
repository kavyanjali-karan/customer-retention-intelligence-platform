# Executive Summary

## Background

Customer churn was identified too late — after the customer had already left. The team had no unified view of customer health, making it impossible to prioritize retention efforts. Revenue at risk was estimated but never quantified with precision.

This project built a churn prediction and retention analytics system that scores 15,000 customers for churn risk, maps each segment to targeted retention actions, and projects 8–12% buyer lifetime value lift on the highest-risk cohort ($554K–$831K annualized impact).

## What This Covers

**Business areas:**
- Customer health (churn prediction, health scoring, engagement)
- Revenue retention (MRR, ARR, revenue at risk)
- Segment analysis (SMB, Mid-Market, Enterprise)
- Retention actions (prioritized recommendations, LTV impact)

**Primary outcome:** A churn prediction model and retention analytics platform consumed by Power BI dashboards and the customer success process.

## Impact

- **Churn prediction:** Scored 15,000 customers for churn risk with segment-level insights
- **Revenue protection:** Identified $611K in ARR at risk ($577K revenue at risk) across the top 50 highest-risk customers
- **LTV optimization:** Projected 8–12% buyer LTV lift producing $554K–$831K annualized impact
- **Dashboard coverage:** 3 SQL-backed dashboards unified by a single DAX measure library

## Key Results

- Built a FastAPI service to score churn risk for 15,000 users and map each segment to targeted retention actions
- Validated 120,000+ transactions and 182,750 activity records with pytest in a GitHub Actions CI pipeline, with Docker Compose for local runs
- Created retention recommendations for 50 at-risk SMB customers with prioritized actions
- Established metric governance standards to align calculations across reports

## Who Uses This

- Executive Leadership (weekly scorecards, monthly business reviews)
- Customer Success (retention actions, health scoring)
- Finance (revenue forecasting, ARR at risk)
- Product (engagement metrics, feature adoption)
