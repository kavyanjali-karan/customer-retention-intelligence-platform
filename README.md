# Customer Retention Intelligence Platform

## Executive Summary

Customer retention is one of the highest leverage business metrics for subscription businesses.

This platform provides governed KPI definitions, executive reporting, semantic analytics, and customer lifecycle intelligence for business stakeholders through a centralized Business Intelligence architecture.

Unlike predictive-only solutions, the platform combines SQL transformation layers, dimensional modeling, Python automation, Power BI semantic models, Tableau dashboards, FastAPI services, and SHAP explanations into a single governed reporting ecosystem.

---

# Business Objectives

- Monitor customer retention trends
- Detect revenue at risk
- Standardize KPI definitions
- Support executive business reviews
- Enable customer lifecycle intelligence
- Deliver explainable retention insights

---

# Stakeholders

Executive Leadership

Finance

Customer Success

Marketing

Product

Business Intelligence Engineering

---

# Business Questions

Which customer segments have the highest churn?

Which regions generate the highest revenue risk?

Which acquisition channels retain customers most effectively?

How much Monthly Recurring Revenue is currently at risk?

Which products demonstrate declining customer health?

---

# KPI Framework

Monthly Recurring Revenue

Retention Rate

Churn Rate

Revenue at Risk

Expansion Revenue

Customer Health Score

Average Revenue Per Customer

Activation Rate

Trial Conversion

---

# Architecture

Raw Data

↓

SQL Staging

↓

Dimension Tables

↓

Fact Table

↓

Business Marts

↓

Metric Layer

↓

Semantic Model

↓

Power BI

↓

Tableau

↓

Executive Business Review

---

# Dimensional Model

Fact

fact_customer_retention

Dimensions

dim_customer

dim_date

dim_product

dim_channel

dim_region

---

# Dashboard Suite

Executive Overview

Customer Health

Cohort Analysis

Revenue at Risk

Churn Analysis

---

# Technology Stack

SQL

Python

FastAPI

Power BI

Tableau

SHAP

Pandas

Scikit-learn

GitHub Actions

---

# Repository Structure

sql/

python/

api/

powerbi/

tableau/

docs/

tests/

data/

models/

assets/

outputs/

---

# Business Intelligence Principles

Single Source of Truth

Reusable Metrics

Semantic Consistency

Star Schema Modeling

Governed KPI Definitions

Executive Decision Support

Operational Monitoring

---

# License

MIT