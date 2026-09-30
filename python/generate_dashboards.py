"""
Generate data-driven Retention dashboard from actual CSV data.

Reads curated CSVs, computes real metrics, and produces
an interactive HTML dashboard with Chart.js.

Usage: python python/generate_dashboards.py
Output: assets/dashboard.html
"""

import csv
import json
import tempfile
from collections import defaultdict
from pathlib import Path

# Chart.js is inlined when a local copy exists (CI downloads one), so the
# dashboard works offline and without depending on a CDN at view time.
CHART_JS = Path(tempfile.gettempdir()) / "chart.min.js"
CHART_JS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
if CHART_JS.exists():
    CHART_JS_TAG = "<script>\n" + CHART_JS.read_text(encoding="utf-8") + "\n</script>"
else:
    CHART_JS_TAG = f'<script src="{CHART_JS_URL}"></script>'


ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "curated"
OUTPUT = ROOT / "assets" / "dashboard.html"


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute_metrics():
    customers = read_csv(DATA_DIR / "dim_customer.csv")
    revenue = read_csv(DATA_DIR / "fact_revenue.csv")
    activity = read_csv(DATA_DIR / "fact_customer_activity.csv")
    retention = read_csv(DATA_DIR / "fact_retention.csv")
    churn = read_csv(DATA_DIR / "churn_predictions.csv")
    targets = read_csv(ROOT / "data" / "warehouse" / "retention_targets.csv")

    total_customers = len(customers)
    total_revenue = sum(float(r["amount"]) for r in revenue)
    total_activity = len(activity)

    # Revenue by month
    monthly_rev = defaultdict(float)
    for r in revenue:
        m = r["transaction_date"][:7]
        monthly_rev[m] += float(r["amount"])
    months_sorted = sorted(monthly_rev.keys())

    # Churn risk
    risk_levels = {"high": 0, "medium": 0, "low": 0}
    for c in churn:
        prob = float(c["churn_probability"])
        if prob >= 0.7:
            risk_levels["high"] += 1
        elif prob >= 0.4:
            risk_levels["medium"] += 1
        else:
            risk_levels["low"] += 1

    # Segment breakdown
    segments = defaultdict(int)
    for c in customers:
        segments[c["segment"]] += 1

    # Retention rate
    retained = sum(1 for r in retention if r["retained_flag"] == "1")
    retention_rate = round(retained / len(retention) * 100, 1) if retention else 0

    # At-risk customers (top 50 by churn probability)
    at_risk = sorted(churn, key=lambda x: -float(x["churn_probability"]))[:50]
    revenue_at_risk = sum(float(c.get("churn_probability", 0)) * 50000 for c in at_risk[:10])

    # Activity metrics
    monthly_activity = defaultdict(int)
    for a in activity:
        m = a["activity_date"][:7]
        monthly_activity[m] += int(a["sessions"])

    return {
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "total_activity": total_activity,
        "months": months_sorted,
        "monthly_rev": [round(monthly_rev[m] / 1000, 1) for m in months_sorted],
        "risk_levels": risk_levels,
        "segments": dict(segments),
        "retention_rate": retention_rate,
        "retained": retained,
        "total_retention": len(retention),
        "revenue_at_risk": revenue_at_risk,
        "at_risk": at_risk[:8],
        "monthly_activity": [monthly_activity.get(m, 0) for m in months_sorted],
    }


def generate_html(m):
    churn_pct = round(m["risk_levels"]["high"] / m["total_customers"] * 100, 1)
    med_pct = round(m["risk_levels"]["medium"] / m["total_customers"] * 100, 1)
    low_pct = round(m["risk_levels"]["low"] / m["total_customers"] * 100, 1)

    risk_rows = ""
    for c in m["at_risk"]:
        prob = round(float(c["churn_probability"]) * 100, 1)
        risk_class = "risk-high" if prob >= 80 else "risk-med"
        risk_rows += f'<tr><td>{c["customer_id"]}</td><td class="{risk_class}">{prob}%</td><td>${50000*float(c["churn_probability"]):,.0f}</td><td>{c.get("top_risk_driver","N/A")}</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Retention Intelligence</title>
    {CHART_JS_TAG}
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f7fa; color: #1e293b; }}
        .topbar {{ background: #0f172a; color: #fff; padding: 10px 24px; display: flex; justify-content: space-between; align-items: center; }}
        .topbar h1 {{ font-size: 15px; font-weight: 600; }}
        .topbar .sub {{ color: #94a3b8; font-size: 11px; }}
        .dash {{ padding: 16px 24px; }}
        .kpi-row {{ display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 16px; }}
        .kpi {{ background: #fff; border-radius: 8px; padding: 16px 18px; box-shadow: 0 1px 2px rgba(0,0,0,0.06); border-left: 4px solid #0ea5e9; }}
        .kpi:nth-child(2) {{ border-left-color: #10b981; }}
        .kpi:nth-child(3) {{ border-left-color: #f59e0b; }}
        .kpi:nth-child(4) {{ border-left-color: #ef4444; }}
        .kpi:nth-child(5) {{ border-left-color: #8b5cf6; }}
        .kpi-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 4px; }}
        .kpi-val {{ font-size: 26px; font-weight: 700; }}
        .kpi-note {{ font-size: 10px; color: #94a3b8; margin-top: 3px; }}
        .row {{ display: grid; gap: 14px; margin-bottom: 16px; }}
        .row-2 {{ grid-template-columns: 3fr 2fr; }}
        .row-eq {{ grid-template-columns: 1fr 1fr; }}
        .box {{ background: #fff; border-radius: 8px; padding: 16px 18px; box-shadow: 0 1px 2px rgba(0,0,0,0.06); }}
        .box-title {{ font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 12px; text-transform: uppercase; }}
        table.dt {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
        table.dt th {{ text-align: left; padding: 7px 8px; background: #f8fafc; border-bottom: 2px solid #e2e8f0; font-weight: 600; color: #64748b; font-size: 10px; text-transform: uppercase; }}
        table.dt td {{ padding: 6px 8px; border-bottom: 1px solid #f1f5f9; }}
        .risk-high {{ color: #dc2626; font-weight: 700; }}
        .risk-med {{ color: #d97706; font-weight: 700; }}
        .footer {{ text-align: center; padding: 14px; font-size: 10px; color: #cbd5e1; }}
    </style>
</head>
<body>
<div class="topbar">
    <h1>&#x1F504; Customer Retention Intelligence Platform</h1>
    <span class="sub">{m['total_customers']:,} customers &middot; {m['total_revenue']/1e6:.0f}K revenue records &middot; {m['total_activity']:,} activity records</span>
</div>
<div class="dash">
    <div class="kpi-row">
        <div class="kpi"><div class="kpi-label">Total Customers</div><div class="kpi-val">{m['total_customers']:,}</div><div class="kpi-note">{len(m['segments'])} segments</div></div>
        <div class="kpi"><div class="kpi-label">Retention Rate</div><div class="kpi-val">{m['retention_rate']}%</div><div class="kpi-note">{m['retained']:,} of {m['total_retention']:,} retained</div></div>
        <div class="kpi"><div class="kpi-label">High Risk Customers</div><div class="kpi-val">{m['risk_levels']['high']:,}</div><div class="kpi-note">{churn_pct}% of base</div></div>
        <div class="kpi"><div class="kpi-label">Revenue at Risk</div><div class="kpi-val">${m['revenue_at_risk']/1e6:.2f}M</div><div class="kpi-note">Top 10 at-risk by ARR</div></div>
        <div class="kpi"><div class="kpi-label">Total Revenue</div><div class="kpi-val">${m['total_revenue']/1e6:.1f}M</div><div class="kpi-note">{m['total_activity']:,} activity records</div></div>
    </div>

    <div class="row row-2">
        <div class="box">
            <div class="box-title">Monthly Revenue Trend ($K)</div>
            <canvas id="revTrend" height="180"></canvas>
        </div>
        <div class="box">
            <div class="box-title">Churn Risk Distribution</div>
            <canvas id="riskDonut" height="180"></canvas>
        </div>
    </div>

    <div class="row row-eq">
        <div class="box">
            <div class="box-title">Customer Segments</div>
            <canvas id="segBar" height="180"></canvas>
        </div>
        <div class="box">
            <div class="box-title">Top 8 At-Risk Customers</div>
            <table class="dt">
                <thead><tr><th>Customer</th><th>Churn Prob</th><th>Rev at Risk</th><th>Top Risk Driver</th></tr></thead>
                <tbody>{risk_rows}</tbody>
            </table>
        </div>
    </div>

    <div class="row row-eq">
        <div class="box">
            <div class="box-title">Monthly Activity (Sessions)</div>
            <canvas id="activityBar" height="200"></canvas>
        </div>
        <div class="box">
            <div class="box-title">Risk Level Breakdown</div>
            <canvas id="riskBar" height="200"></canvas>
        </div>
    </div>
</div>
<div class="footer">Customer Retention Intelligence &middot; FastAPI &middot; pytest &middot; Docker &middot; GitHub Actions &middot; Power BI</div>

<script>
const months = {json.dumps([mm[-5:] for mm in m['months']])};

new Chart(document.getElementById('revTrend'), {{
    type: 'line',
    data: {{ labels: months, datasets: [{{ label: 'Revenue ($K)', data: {json.dumps(m['monthly_rev'])}, borderColor: '#0ea5e9', backgroundColor: 'rgba(14,165,233,0.08)', fill: true, tension: 0.3, pointRadius: 3, borderWidth: 2 }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ ticks: {{ callback: v => '$'+v+'K' }}, grid: {{ color: '#f1f5f9' }} }}, x: {{ grid: {{ display: false }} }} }} }}
}});

new Chart(document.getElementById('riskDonut'), {{
    type: 'doughnut',
    data: {{ labels: ['Low ({low_pct}%)','Medium ({med_pct}%)','High ({churn_pct}%)'], datasets: [{{ data: {json.dumps(list(m['risk_levels'].values()))}, backgroundColor: ['#10b981','#f59e0b','#ef4444'], borderWidth: 2, borderColor: '#fff' }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 10, font: {{ size: 10 }} }} }} }} }}
}});

new Chart(document.getElementById('segBar'), {{
    type: 'bar',
    data: {{ labels: {json.dumps(list(m['segments'].keys()))}, datasets: [{{ data: {json.dumps(list(m['segments'].values()))}, backgroundColor: ['#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6'], borderRadius: 3 }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#f1f5f9' }} }}, x: {{ grid: {{ display: false }} }} }} }}
}});

new Chart(document.getElementById('activityBar'), {{
    type: 'bar',
    data: {{ labels: months, datasets: [{{ label: 'Sessions', data: {json.dumps(m['monthly_activity'])}, backgroundColor: 'rgba(14,165,233,0.6)', borderRadius: 2 }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#f1f5f9' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 45 }} }} }} }}
}});

new Chart(document.getElementById('riskBar'), {{
    type: 'bar',
    data: {{ labels: ['Low','Medium','High'], datasets: [{{ data: {json.dumps(list(m['risk_levels'].values()))}, backgroundColor: ['#10b981','#f59e0b','#ef4444'], borderRadius: 3 }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#f1f5f9' }} }}, x: {{ grid: {{ display: false }} }} }} }}
}});
</script>
</body>
</html>"""


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    m = compute_metrics()
    html = generate_html(m)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Dashboard generated: {OUTPUT}")
    print(f"  Customers: {m['total_customers']:,} | Retention: {m['retention_rate']}%")
    print(f"  Revenue: ${m['total_revenue']/1e6:.1f}M | High Risk: {m['risk_levels']['high']:,}")


if __name__ == "__main__":
    main()
