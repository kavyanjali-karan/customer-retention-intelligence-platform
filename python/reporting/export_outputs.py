"""Regenerate every file in outputs/ from the curated data.

The outputs/ folder holds the deliverables described in README.md. They are
derived, not hand-made: run this script after data/generate_data.py and the
CSVs will match the data exactly.

Usage:
    python python/reporting/export_outputs.py
Output:
    outputs/*.csv
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CURATED = ROOT / "data" / "curated"
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"


def action_for(probability: float) -> str:
    if probability >= 0.80:
        return "Immediate outreach - high-touch save play"
    if probability >= 0.65:
        return "Assign CSM - quarterly business review"
    return "Monitor - automated nurture"


def main() -> None:
    OUT.mkdir(exist_ok=True)

    churn = pd.read_csv(CURATED / "churn_predictions.csv")
    health = pd.read_csv(CURATED / "customer_health_scores.csv")
    risk = pd.read_csv(CURATED / "revenue_at_risk.csv")
    customers = pd.read_csv(CURATED / "dim_customer.csv")
    revenue = pd.read_csv(CURATED / "fact_revenue.csv", parse_dates=["transaction_date"])
    activity = pd.read_csv(RAW / "customer_activity.csv", parse_dates=["activity_date"])
    retention = pd.read_csv(CURATED / "fact_retention.csv")

    # ------------------------------------------------------------------
    # churn_risk_export.csv - all customers, scored
    # ------------------------------------------------------------------
    churn_out = churn[["customer_id", "churn_probability", "top_risk_driver"]].rename(
        columns={"churn_probability": "Sum of churn_probability"}
    )
    churn_out.to_csv(OUT / "churn_risk_export.csv", index=False)

    # ------------------------------------------------------------------
    # revenue_at_risk_export.csv - per-customer exposure
    # ------------------------------------------------------------------
    risk_out = risk[["current_arr", "customer_id", "revenue_at_risk"]].rename(
        columns={
            "current_arr": "Sum of current_arr",
            "revenue_at_risk": "Sum of revenue_at_risk",
        }
    )[["Sum of current_arr", "customer_id", "Sum of revenue_at_risk"]]
    risk_out.to_csv(OUT / "revenue_at_risk_export.csv", index=False)

    # ------------------------------------------------------------------
    # customer_health_export.csv - customers by health band
    # ------------------------------------------------------------------
    health_counts = (
        health.groupby("health_band")
        .size()
        .rename("Count of customer_id")
        .reset_index()[["Count of customer_id", "health_band"]]
        .sort_values("Count of customer_id", ascending=False)
    )
    health_counts.to_csv(OUT / "customer_health_export.csv", index=False)

    # ------------------------------------------------------------------
    # retention_recommendations.csv - top 50 at-risk SMB customers
    # ------------------------------------------------------------------
    smb = customers.loc[customers["segment"].eq("SMB"), ["customer_id", "segment"]]
    recommendations = (
        smb.merge(churn, on="customer_id")
        .merge(risk[["customer_id", "revenue_at_risk"]], on="customer_id")
        .sort_values("churn_probability", ascending=False)
        .head(50)
        .copy()
    )
    recommendations["recommended_action"] = recommendations["churn_probability"].map(action_for)
    recommendations["priority"] = range(1, len(recommendations) + 1)
    recommendations[
        [
            "priority",
            "customer_id",
            "segment",
            "churn_probability",
            "revenue_at_risk",
            "top_risk_driver",
            "recommended_action",
        ]
    ].to_csv(OUT / "retention_recommendations.csv", index=False)

    # ------------------------------------------------------------------
    # ltv_impact_summary.csv - cohort value and the LTV lift range
    # ------------------------------------------------------------------
    cohort = recommendations
    cohort_arr = retention.loc[
        retention["customer_id"].isin(cohort["customer_id"]), "arr"
    ].sum()
    cohort_risk = cohort["revenue_at_risk"].sum()
    summary = pd.DataFrame(
        [
            ["Target Cohort Size", float(len(cohort)),
             "SMB customers with >65% churn probability"],
            ["Cohort Total ARR", float(cohort_arr), "USD"],
            ["Cohort Revenue at Risk", float(round(cohort_risk, 2)), "USD"],
            ["Projected LTV Lift (Low - 8%)", float(round(cohort_risk * 0.08, 2)),
             "USD per month"],
            ["Projected LTV Lift (High - 12%)", float(round(cohort_risk * 0.12, 2)),
             "USD per month"],
        ],
        columns=["metric", "value", "unit"],
    )
    summary.to_csv(OUT / "ltv_impact_summary.csv", index=False)

    # ------------------------------------------------------------------
    # executive_business_review.csv - monthly executive rollup
    # ------------------------------------------------------------------
    revenue["month"] = revenue["transaction_date"].dt.strftime("%Y-%m")
    activity["month"] = activity["activity_date"].dt.strftime("%Y-%m")

    monthly_revenue = revenue.groupby("month").agg(
        revenue=("amount", "sum"), transactions=("transaction_id", "count")
    )
    monthly_active = activity.groupby("month").agg(
        active_customers=("customer_id", "nunique")
    )
    monthly = monthly_revenue.join(monthly_active, how="outer").fillna(0)
    monthly["revenue_per_customer"] = (
        monthly["revenue"] / monthly["active_customers"].replace(0, pd.NA)
    ).round(2)
    monthly.reset_index().to_csv(OUT / "executive_business_review.csv", index=False)

    # ------------------------------------------------------------------
    # quarterly_business_review.csv - quarterly aggregation with trend
    # ------------------------------------------------------------------
    quarterly_revenue = revenue.groupby(revenue["transaction_date"].dt.to_period("Q")).agg(
        revenue=("amount", "sum"), transactions=("transaction_id", "count")
    )
    activity_q = activity.groupby(activity["activity_date"].dt.to_period("Q")).agg(
        active_customers=("customer_id", "nunique")
    )
    quarterly = quarterly_revenue.join(activity_q, how="outer").fillna(0)
    quarterly.index = quarterly.index.astype(str)
    quarterly["revenue_qoq_pct"] = (
        quarterly["revenue"].pct_change(fill_method=None) * 100
    ).round(1)
    quarterly["transactions_qoq_pct"] = (
        quarterly["transactions"].pct_change(fill_method=None) * 100
    ).round(1)
    quarterly.reset_index(names="quarter").to_csv(
        OUT / "quarterly_business_review.csv", index=False
    )

    for name in sorted(OUT.glob("*.csv")):
        print(f"OK {name.name} ({sum(1 for _ in name.open(encoding='utf-8-sig')) - 1} rows)")
    print(f"\nAll deliverables written to {OUT}")


if __name__ == "__main__":
    main()
