"""
visual_report.py
-----------------
Builds ONE composite "visual report" image (charts/00_visual_report.png)
that combines the most important charts and headline numbers on a
single page -- a quick static dashboard you can open without running
Streamlit.

Run with:  python visual_report.py   (after visualization.py)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

df = pd.read_csv("cleaned_dataset.csv", parse_dates=["OrderDate"])

total_revenue = df["Revenue"].sum()
total_orders = len(df)
avg_order_value = df["Revenue"].mean()
avg_rating = df["Rating"].mean()
top_category = df.groupby("ProductCategory")["Revenue"].sum().idxmax()

fig = plt.figure(figsize=(15, 9))
fig.suptitle("Online Retail Orders - Data Cleaning & Visualization Report",
             fontsize=16, fontweight="bold")

# --- KPI strip -----------------------------------------------------
kpi_ax = fig.add_axes([0.02, 0.90, 0.96, 0.06])
kpi_ax.axis("off")
kpis = [
    f"Total Orders: {total_orders:,}",
    f"Total Revenue: Rs. {total_revenue:,.0f}",
    f"Avg Order Value: Rs. {avg_order_value:,.0f}",
    f"Avg Rating: {avg_rating:.2f} / 5",
    f"Top Category: {top_category}",
]
kpi_ax.text(0.5, 0.5, "    |    ".join(kpis), ha="center", va="center", fontsize=11.5, fontweight="bold")

gs = fig.add_gridspec(2, 3, top=0.85, bottom=0.08, hspace=0.45, wspace=0.35)

# 1. Revenue by category
ax1 = fig.add_subplot(gs[0, 0])
rev_cat = df.groupby("ProductCategory")["Revenue"].sum().sort_values(ascending=False)
sns.barplot(x=rev_cat.index, y=rev_cat.values, hue=rev_cat.index, palette="viridis", legend=False, ax=ax1)
ax1.set_title("Revenue by Category", fontweight="bold")
ax1.set_xlabel("")
ax1.set_ylabel("Revenue (Rs.)")
ax1.tick_params(axis="x", rotation=30)

# 2. Monthly revenue trend
ax2 = fig.add_subplot(gs[0, 1])
monthly = df.groupby("OrderMonth")["Revenue"].sum().sort_index()
ax2.plot(monthly.index, monthly.values, marker="o", color="#2a6f97")
ax2.set_title("Monthly Revenue Trend", fontweight="bold")
ax2.set_xlabel("")
ax2.set_ylabel("Revenue (Rs.)")
ax2.tick_params(axis="x", rotation=60, labelsize=7)

# 3. Age distribution
ax3 = fig.add_subplot(gs[0, 2])
sns.histplot(df["Age"], bins=15, kde=True, color="#e07a5f", ax=ax3)
ax3.set_title("Customer Age Distribution", fontweight="bold")
ax3.set_xlabel("Age")

# 4. Boxplot price by category
ax4 = fig.add_subplot(gs[1, 0])
sns.boxplot(data=df, x="ProductCategory", y="Price", hue="ProductCategory",
            palette="Set2", legend=False, ax=ax4)
ax4.set_title("Price Spread by Category", fontweight="bold")
ax4.set_xlabel("")
ax4.set_ylabel("Price (Rs.)")
ax4.tick_params(axis="x", rotation=30)

# 5. Scatter age vs revenue
ax5 = fig.add_subplot(gs[1, 1])
sns.scatterplot(data=df, x="Age", y="Revenue", hue="ProductCategory",
                 palette="tab10", alpha=0.7, s=30, legend=False, ax=ax5)
ax5.set_title("Age vs Revenue", fontweight="bold")

# 6. Correlation heatmap
ax6 = fig.add_subplot(gs[1, 2])
numeric_cols = ["Age", "Price", "Quantity", "Rating", "Revenue"]
sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm",
            cbar=False, ax=ax6, annot_kws={"size": 8})
ax6.set_title("Correlation Heatmap", fontweight="bold")

plt.savefig("charts/00_visual_report.png", dpi=130, bbox_inches="tight")
plt.close()
print("Saved combined visual report to charts/00_visual_report.png")
