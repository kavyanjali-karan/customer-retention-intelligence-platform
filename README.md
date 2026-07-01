````markdown
# Customer Retention Intelligence Platform

A production-style Business Intelligence reporting system designed to transform operational customer data into governed analytical datasets for customer lifecycle reporting, retention analysis, and executive decision-making.

---

## Why This Reporting System Exists

Customer retention depends on understanding how customer behavior evolves over time rather than measuring churn as a single outcome. Reliable reporting requires consistent business metrics, standardized data preparation, and analytical models that support recurring business decisions.

This repository demonstrates how operational customer data can be transformed into curated reporting datasets through SQL, Python ETL, dimensional modeling, semantic modeling, and engineering documentation before it reaches Power BI.

---

## Business Domain

The reporting workflow focuses on measuring customer retention across the complete customer lifecycle.

The reporting model supports analysis across:

- Customer activity
- Customer health
- Customer retention
- Revenue at Risk
- Cohort performance
- Product adoption
- Regional performance
- Acquisition channel performance

Instead of treating reporting as individual dashboards, the repository organizes business reporting around reusable analytical datasets and standardized KPI definitions.

---

## Reporting Architecture

```text
Operational Customer Data
           │
           ▼
SQL Transformation
           │
           ▼
Python ETL & Data Validation
           │
           ▼
Curated Analytical Layer
           │
           ▼
Dimensional Model
           │
           ▼
Power BI Semantic Model
           │
           ▼
Executive Reporting
```

The reporting workflow separates transformation, business logic, analytical modeling, and visualization into independent layers that support maintainable Business Intelligence reporting.

---

## Repository Structure

```text
customer-retention-intelligence-platform/

├── api/
├── data/
│   ├── raw/
│   ├── curated/
│   └── warehouse/
│
├── sql/
├── python/
├── powerbi/
├── documentation/
├── outputs/
└── README.md
```

The repository organizes reporting assets, transformation logic, analytical datasets, documentation, and API services into clearly separated components.

---

## Analytical Model

Customer retention reporting is organized around a dimensional model that separates descriptive business entities from measurable customer activity.

### Dimensions

- Customer
- Product
- Region
- Channel
- Date

### Reporting Facts

The reporting model captures business activity across:

- Customer Activity
- Customer Retention
- Revenue Performance

This dimensional structure enables consistent reporting across executive dashboards, cohort analysis, customer health monitoring, and revenue reporting.

---

## Data Preparation

Operational customer data is transformed through SQL and Python before being loaded into the reporting model.

The preparation workflow includes:

- Data cleansing
- Business rule standardization
- Data validation
- Curated analytical datasets
- Reporting-ready outputs

Preparing business logic before visualization helps maintain consistent reporting across analytical assets.

---

## API Services

The repository extends beyond reporting by exposing customer retention functionality through a dedicated FastAPI layer.

Available services support:

- Retention analysis
- Customer recommendations
- Business metrics
- Health monitoring
- Explainable retention insights

The API layer allows analytical outputs to be consumed independently from reporting dashboards while maintaining consistent business logic.

---

## Power BI Reporting

Power BI consumes curated analytical datasets through a semantic model designed for customer retention reporting.

Reporting assets focus on:

- Executive KPI monitoring
- Customer health
- Cohort analysis
- Revenue at Risk
- Retention trends
- Product performance
- Regional analysis
- Channel performance

Business calculations remain centralized within the reporting model to ensure metric consistency across reports.

---

## Business Documentation

Engineering documentation is maintained alongside implementation and includes:

- Reporting architecture
- Business context
- Metric dictionary
- Business glossary
- Data dictionary
- Reporting playbook
- Weekly Business Review
- Executive summary
- Data quality documentation

Documentation forms part of the reporting solution by providing consistent definitions for business metrics and reporting standards.

---

## Engineering Decisions

The reporting system is designed around several core engineering principles.

- Transform operational data before reporting.
- Standardize business metrics through curated analytical datasets.
- Separate business logic from visualization.
- Organize reporting through dimensional modeling.
- Document reporting standards alongside implementation.
- Reuse governed datasets across reporting assets and API services.

---

## Technology

**Reporting**

- Power BI
- DAX
- Power Query

**Data Engineering**

- SQL
- Python
- ETL
- Data Validation

**Modeling**

- Dimensional Modeling
- Semantic Modeling

**Application**

- FastAPI

**Engineering**

- Reporting Architecture
- KPI Governance
- Business Documentation
- Git
- GitHub

---

## Portfolio Context

This repository is part of a Business Intelligence Engineering portfolio demonstrating how reporting systems are designed through reporting architecture, SQL transformation, Python ETL, dimensional modeling, KPI governance, semantic modeling, and executive reporting.

Related repositories:

- Executive KPI Governance Platform
- Growth Funnel Performance Review
- Marketplace Growth Performance Review

Together, these repositories demonstrate reporting systems across customer retention, KPI governance, growth analytics, and marketplace performance while following a consistent Business Intelligence engineering approach.

---

## Author

**Kavyanjali Karan**

Computer Science student building production-style Business Intelligence reporting systems with a focus on reporting architecture, dimensional modeling, KPI governance, semantic modeling, and engineering documentation.

---

## Engineering Outcomes

This repository demonstrates the ability to:

- Design analytical models focused on customer retention, engagement, and behavioral reporting.
- Prepare curated datasets that support retention analysis through repeatable SQL and Python transformation workflows.
- Structure business metrics that enable consistent reporting of customer activity, segmentation, and retention trends.
- Separate data engineering, analytical modeling, and reporting responsibilities into reusable project components.
- Document reporting logic and repository organization to support reproducible Business Intelligence workflows.

````
