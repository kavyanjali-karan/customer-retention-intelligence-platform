"""
Generate Power BI-style dashboard visuals from project data.

Reads curated CSVs and produces high-resolution PNG dashboards
with a dark theme matching the executive-kpi-governance-platform style.

Usage: python python/generate_dashboard_pngs.py
Output: assets/*.png (5 dashboards)
"""

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Paths
BASE = Path(__file__).resolve().parents[1]
CURATED = BASE / "data" / "curated"
WH = BASE / "data" / "warehouse"
ASSETS = BASE / "assets"
ASSETS.mkdir(exist_ok=True)

# Load data
customers = pd.read_csv(CURATED / "dim_customer.csv")
revenue = pd.read_csv(CURATED / "fact_revenue.csv")
activity = pd.read_csv(CURATED / "fact_customer_activity.csv")
health = pd.read_csv(CURATED / "customer_health_scores.csv")
churn = pd.read_csv(CURATED / "churn_predictions.csv")
retention = pd.read_csv(CURATED / "fact_retention.csv")
cohorts = pd.read_csv(CURATED / "retention_cohorts.csv")
risk = pd.read_csv(CURATED / "revenue_at_risk.csv")

# Merge
df = revenue.merge(customers[["customer_id", "segment", "industry"]], on="customer_id", how="left")
df["txn_date"] = pd.to_datetime(df["transaction_date"])
df["month"] = df["txn_date"].dt.to_period("M").astype(str)

# Monthly aggregates
monthly = df.groupby("month").agg(
    revenue=("amount", "sum"),
    transactions=("transaction_id", "count"),
    unique_customers=("customer_id", "nunique"),
).reset_index().sort_values("month")

# Revenue by type
rev_type = df.groupby("revenue_type")["amount"].sum().sort_values(ascending=False)

# Segment breakdown
seg_rev = df.groupby("segment")["amount"].sum().sort_values(ascending=True)

# Industry breakdown
ind_rev = df.groupby("industry")["amount"].sum().sort_values(ascending=True)

# Health distribution
health_dist = health["health_band"].value_counts()

# Churn risk
churn_flagged = churn["predicted_churn_flag"].sum()
churn_rate = churn_flagged / len(churn) * 100

# Revenue at risk
top_risk = risk.nlargest(10, "revenue_at_risk")

# Cohort retention
cohort_pivot = cohorts.pivot(index="cohort_month", columns="month_number", values="retention_rate")

# Theme
BG = "#151029"
CARD_BG = "#1F1940"
TEXT = "#EDEAF7"
MUTED = "#9A93BE"
ACCENT1 = "#8B7CFF"
ACCENT2 = "#FF6E9C"
ACCENT3 = "#5EEAD4"
ACCENT4 = "#FDBA74"
ACCENT5 = "#60A5FA"
GRID = "#332B5E"
PALETTE = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, "#C084FC", "#F472B6", "#F9A8D4"]


def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(CARD_BG)
    ax.set_title(title, color=TEXT, fontsize=14, fontweight="bold", pad=10, loc="left")
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.5, alpha=0.5)


def fmt_k(x, _=None):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.0f}K"
    return f"${x:.0f}"


# Dashboard 1 - Executive Overview
def create_executive_overview():
    latest = monthly.iloc[-1]
    total_rev = monthly["revenue"].sum()
    avg_monthly = monthly["revenue"].mean()
    total_txn = monthly["transactions"].sum()
    avg_customers = monthly["unique_customers"].mean()

    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    fig.suptitle("Executive Overview", color=TEXT, fontsize=20, fontweight="bold", y=0.97, x=0.04, ha="left")
    fig.text(0.04, 0.945, f"15,000 customers  |  ${total_rev/1e6:.1f}M total revenue  |  {len(monthly)} months",
             color=MUTED, fontsize=10, ha="left")

    # KPI cards
    card_data = [
        ("Total Revenue", f"${total_rev/1e6:.1f}M", f"Avg ${avg_monthly/1e6:.1f}M/mo", ACCENT1),
        ("Customers", "15,000", f"{health_dist.get('Healthy', 0):,} healthy", ACCENT4),
        ("Churn Risk", f"{churn_rate:.1f}%", f"{churn_flagged:,} flagged", ACCENT3),
        ("Revenue at Risk", f"${risk['revenue_at_risk'].sum()/1e6:.1f}M", f"Top 10: ${top_risk['revenue_at_risk'].sum()/1e6:.1f}M", ACCENT5),
        ("Transactions", f"{total_txn:,}", f"{avg_customers:.0f} avg customers/mo", ACCENT2),
    ]

    for i, (label, value, sub, color) in enumerate(card_data):
        x = 0.04 + i * 0.19
        rect = FancyBboxPatch((x, 0.87), 0.17, 0.055, boxstyle="round,pad=0.008",
                              facecolor=CARD_BG, edgecolor=color, linewidth=1.5, transform=fig.transFigure)
        fig.patches.append(rect)
        fig.text(x + 0.085, 0.912, value, color=color, fontsize=18, fontweight="bold", ha="center", va="center")
        fig.text(x + 0.085, 0.895, label, color=MUTED, fontsize=9, ha="center", va="center")
        fig.text(x + 0.085, 0.878, sub, color=MUTED, fontsize=8, ha="center", va="center")

    # Revenue trend
    ax1 = fig.add_axes([0.04, 0.48, 0.44, 0.35])
    style_ax(ax1, "Monthly Revenue", ylabel="Revenue")
    ax1.fill_between(range(len(monthly)), monthly["revenue"], alpha=0.15, color=ACCENT1)
    ax1.plot(range(len(monthly)), monthly["revenue"], color=ACCENT1, linewidth=2)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
    ax1.set_xticks(range(0, len(monthly), 4))
    ax1.set_xticklabels([monthly["month"].iloc[i] for i in range(0, len(monthly), 4)], rotation=0, fontsize=7)

    # Revenue by type
    ax2 = fig.add_axes([0.52, 0.48, 0.44, 0.35])
    style_ax(ax2, "Revenue by Type")
    colors = [ACCENT1, ACCENT4, ACCENT2, ACCENT3, ACCENT5]
    bars = ax2.barh(rev_type.index, rev_type.values, color=colors[:len(rev_type)], height=0.6)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
    for bar, val in zip(bars, rev_type.values):
        ax2.text(val + rev_type.max() * 0.02, bar.get_y() + bar.get_height()/2,
                 fmt_k(val), color=TEXT, fontsize=8, va="center")

    # Segment breakdown
    ax3 = fig.add_axes([0.04, 0.06, 0.2, 0.35])
    style_ax(ax3, "Revenue by Segment")
    bars = ax3.barh(seg_rev.index, seg_rev.values, color=PALETTE[:len(seg_rev)], height=0.55)
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))

    # Industry breakdown
    ax4 = fig.add_axes([0.27, 0.06, 0.21, 0.35])
    style_ax(ax4, "Revenue by Industry")
    bars = ax4.barh(ind_rev.index, ind_rev.values, color=PALETTE[:len(ind_rev)], height=0.55)
    ax4.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))

    # Health distribution
    ax5 = fig.add_axes([0.52, 0.06, 0.44, 0.35])
    style_ax(ax5, "Customer Health Distribution")
    health_colors = {"Healthy": ACCENT4, "At Risk": ACCENT5, "Critical": ACCENT3}
    bars = ax5.bar(health_dist.index, health_dist.values,
                   color=[health_colors.get(b, MUTED) for b in health_dist.index], width=0.55)
    for bar, val in zip(bars, health_dist.values):
        ax5.text(bar.get_x() + bar.get_width()/2, val + 50, f"{val:,}", color=TEXT, fontsize=9, ha="center")

    fig.savefig(ASSETS / "executive_overview.png", dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("OK executive_overview.png")


# Dashboard 2 - Customer Health
def create_customer_health():
    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    fig.suptitle("Customer Health", color=TEXT, fontsize=20, fontweight="bold", y=0.97, x=0.04, ha="left")
    fig.text(0.04, 0.945, f"Health scores for 15,000 customers  |  {churn_rate:.1f}% churn risk  |  Engagement, support, and revenue signals",
             color=MUTED, fontsize=10, ha="left")

    # Health score distribution
    ax1 = fig.add_axes([0.04, 0.52, 0.44, 0.38])
    style_ax(ax1, "Health Score Distribution", xlabel="Health Score")
    ax1.hist(health["health_score"], bins=40, color=ACCENT1, alpha=0.7, edgecolor=CARD_BG, linewidth=0.5)
    ax1.axvline(x=health["health_score"].mean(), color=ACCENT5, linestyle="--", linewidth=1.5,
                label=f'Mean: {health["health_score"].mean():.1f}')
    ax1.legend(fontsize=8, loc="upper left", framealpha=0.3, facecolor=CARD_BG, edgecolor=GRID, labelcolor=TEXT)

    # Health by segment
    ax2 = fig.add_axes([0.52, 0.52, 0.44, 0.38])
    style_ax(ax2, "Avg Health Score by Segment")
    seg_health = health.merge(customers[["customer_id", "segment"]], on="customer_id").groupby("segment")["health_score"].mean().sort_values(ascending=True)
    bars = ax2.barh(seg_health.index, seg_health.values, color=PALETTE[:len(seg_health)], height=0.55)
    for bar, val in zip(bars, seg_health.values):
        ax2.text(val + 0.5, bar.get_y() + bar.get_height()/2, f"{val:.1f}", color=TEXT, fontsize=9, va="center")

    # Churn probability distribution
    ax3 = fig.add_axes([0.04, 0.06, 0.44, 0.38])
    style_ax(ax3, "Churn Probability Distribution", xlabel="Churn Probability")
    ax3.hist(churn["churn_probability"], bins=40, color=ACCENT3, alpha=0.7, edgecolor=CARD_BG, linewidth=0.5)
    ax3.axvline(x=0.5, color=ACCENT5, linestyle="--", linewidth=1.5, label="Threshold: 0.5")
    ax3.legend(fontsize=8, loc="upper right", framealpha=0.3, facecolor=CARD_BG, edgecolor=GRID, labelcolor=TEXT)

    # Top risk drivers
    ax4 = fig.add_axes([0.52, 0.06, 0.44, 0.38])
    style_ax(ax4, "Top Churn Risk Drivers")
    drivers = churn["top_risk_driver"].value_counts().head(8)
    bars = ax4.barh(drivers.index, drivers.values, color=PALETTE[:len(drivers)], height=0.55)
    for bar, val in zip(bars, drivers.values):
        ax4.text(val + 20, bar.get_y() + bar.get_height()/2, f"{val:,}", color=TEXT, fontsize=8, va="center")

    fig.savefig(ASSETS / "customer_health.png", dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("OK customer_health.png")


# Dashboard 3 - Cohort Analysis
def create_cohort_analysis():
    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    fig.suptitle("Cohort Retention Analysis", color=TEXT, fontsize=20, fontweight="bold", y=0.97, x=0.04, ha="left")
    fig.text(0.04, 0.945, f"{len(cohort_pivot)} cohorts  |  Monthly retention tracking  |  12-month follow-up",
             color=MUTED, fontsize=10, ha="left")

    # Retention heatmap
    ax1 = fig.add_axes([0.04, 0.15, 0.92, 0.72])
    style_ax(ax1, "Retention Rate by Cohort Month")
    data = cohort_pivot.values
    im = ax1.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax1.set_xticks(range(data.shape[1]))
    ax1.set_xticklabels([f"M{i}" for i in range(data.shape[1])], color=MUTED, fontsize=8)
    ax1.set_yticks(range(data.shape[0]))
    ax1.set_yticklabels(cohort_pivot.index, color=MUTED, fontsize=8)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if not np.isnan(val):
                ax1.text(j, i, f"{val:.0f}%", ha="center", va="center", color=TEXT, fontsize=7)
    cbar = plt.colorbar(im, ax=ax1, shrink=0.8)
    cbar.ax.tick_params(colors=MUTED, labelsize=8)

    fig.savefig(ASSETS / "cohort_analysis.png", dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("OK cohort_analysis.png")


# Dashboard 4 - Revenue at Risk
def create_revenue_at_risk():
    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    fig.suptitle("Revenue at Risk", color=TEXT, fontsize=20, fontweight="bold", y=0.97, x=0.04, ha="left")
    total_risk = risk["revenue_at_risk"].sum()
    fig.text(0.04, 0.945, f"${total_risk/1e6:.1f}M total exposure  |  {len(risk[risk['revenue_at_risk'] > 0]):,} customers with risk  |  Top 10 accounts",
             color=MUTED, fontsize=10, ha="left")

    # Risk distribution
    ax1 = fig.add_axes([0.04, 0.52, 0.44, 0.38])
    style_ax(ax1, "Revenue at Risk Distribution", xlabel="Revenue at Risk ($)")
    risk_positive = risk[risk["revenue_at_risk"] > 0]["revenue_at_risk"]
    ax1.hist(risk_positive, bins=50, color=ACCENT3, alpha=0.7, edgecolor=CARD_BG, linewidth=0.5)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))

    # Top 10 accounts
    ax2 = fig.add_axes([0.52, 0.52, 0.44, 0.38])
    style_ax(ax2, "Top 10 Accounts by Revenue at Risk")
    bars = ax2.barh(top_risk["customer_id"], top_risk["revenue_at_risk"], color=ACCENT3, height=0.6, alpha=0.8)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
    for bar, val in zip(bars, top_risk["revenue_at_risk"]):
        ax2.text(val + top_risk["revenue_at_risk"].max() * 0.02, bar.get_y() + bar.get_height()/2,
                 fmt_k(val), color=TEXT, fontsize=8, va="center")

    # Risk by segment
    ax3 = fig.add_axes([0.04, 0.06, 0.44, 0.38])
    style_ax(ax3, "Revenue at Risk by Segment")
    risk_seg = risk.merge(customers[["customer_id", "segment"]], on="customer_id").groupby("segment")["revenue_at_risk"].sum().sort_values(ascending=True)
    bars = ax3.barh(risk_seg.index, risk_seg.values, color=PALETTE[:len(risk_seg)], height=0.55)
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
    for bar, val in zip(bars, risk_seg.values):
        ax3.text(val + risk_seg.max() * 0.02, bar.get_y() + bar.get_height()/2,
                 fmt_k(val), color=TEXT, fontsize=8, va="center")

    # Risk percentage vs ARR
    ax4 = fig.add_axes([0.52, 0.06, 0.44, 0.38])
    style_ax(ax4, "Risk % vs Current ARR", xlabel="Current ARR ($)", ylabel="Risk %")
    ax4.scatter(risk["current_arr"], risk["risk_percentage"], alpha=0.3, s=10, color=ACCENT2)
    ax4.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
    ax4.yaxis.set_major_formatter(mticker.PercentFormatter())

    fig.savefig(ASSETS / "revenue_at_risk.png", dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("OK revenue_at_risk.png")


# Dashboard 5 - Churn Analysis
def create_churn_analysis():
    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    fig.suptitle("Churn Analysis", color=TEXT, fontsize=20, fontweight="bold", y=0.97, x=0.04, ha="left")
    fig.text(0.04, 0.945, f"{churn_flagged:,} customers flagged for churn  |  {churn_rate:.1f}% risk rate  |  Risk driver analysis",
             color=MUTED, fontsize=10, ha="left")

    # Churn by segment
    ax1 = fig.add_axes([0.04, 0.52, 0.44, 0.38])
    style_ax(ax1, "Churn Risk by Segment")
    churn_seg = churn.merge(customers[["customer_id", "segment"]], on="customer_id").groupby("segment")["predicted_churn_flag"].mean() * 100
    churn_seg = churn_seg.sort_values(ascending=True)
    bars = ax1.barh(churn_seg.index, churn_seg.values, color=PALETTE[:len(churn_seg)], height=0.55)
    ax1.xaxis.set_major_formatter(mticker.PercentFormatter())
    for bar, val in zip(bars, churn_seg.values):
        ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", color=TEXT, fontsize=9, va="center")

    # Churn by industry
    ax2 = fig.add_axes([0.52, 0.52, 0.44, 0.38])
    style_ax(ax2, "Churn Risk by Industry")
    churn_ind = churn.merge(customers[["customer_id", "industry"]], on="customer_id").groupby("industry")["predicted_churn_flag"].mean() * 100
    churn_ind = churn_ind.sort_values(ascending=True)
    bars = ax2.barh(churn_ind.index, churn_ind.values, color=PALETTE[:len(churn_ind)], height=0.55)
    ax2.xaxis.set_major_formatter(mticker.PercentFormatter())
    for bar, val in zip(bars, churn_ind.values):
        ax2.text(val + 0.3, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", color=TEXT, fontsize=9, va="center")

    # Churn probability by health band
    ax3 = fig.add_axes([0.04, 0.06, 0.44, 0.38])
    style_ax(ax3, "Churn Probability by Health Band")
    merged = churn.merge(health[["customer_id", "health_band"]], on="customer_id")
    health_order = ["Healthy", "At Risk", "Critical"]
    health_data = [merged[merged["health_band"] == h]["churn_probability"].values for h in health_order if h in merged["health_band"].values]
    health_labels = [h for h in health_order if h in merged["health_band"].values]
    bp = ax3.boxplot(health_data, tick_labels=health_labels, patch_artist=True)
    for patch, color in zip(bp["boxes"], [ACCENT4, ACCENT5, ACCENT3]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    for median in bp["medians"]:
        median.set_color(TEXT)

    # Risk driver breakdown
    ax4 = fig.add_axes([0.52, 0.06, 0.44, 0.38])
    style_ax(ax4, "Churn Risk Driver Breakdown")
    drivers = churn["top_risk_driver"].value_counts()
    colors = PALETTE[:len(drivers)]
    wedges, texts, autotexts = ax4.pie(drivers.values, labels=drivers.index,
                                        colors=colors, autopct="%1.0f%%",
                                        textprops={"color": TEXT, "fontsize": 9},
                                        pctdistance=0.75, startangle=90)
    for at in autotexts:
        at.set_fontsize(8)

    fig.savefig(ASSETS / "churn_analysis.png", dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("OK churn_analysis.png")


if __name__ == "__main__":
    print("Generating retention dashboards...")
    create_executive_overview()
    create_customer_health()
    create_cohort_analysis()
    create_revenue_at_risk()
    create_churn_analysis()
    print(f"\nAll dashboards saved to {ASSETS}/")
