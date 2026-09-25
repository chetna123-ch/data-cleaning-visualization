"""
visualization.py
-----------------
Loads cleaned_dataset.csv and creates all required visualizations
using Matplotlib & Seaborn. Each chart is saved as a PNG inside
the charts/ folder.

Run with:  python visualization.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

os.makedirs("charts", exist_ok=True)

df = pd.read_csv("cleaned_dataset.csv", parse_dates=["OrderDate"])

# -----------------------------------------------------------------
# 1. BAR CHART - Total Revenue by Product Category
# -----------------------------------------------------------------
revenue_by_cat = df.groupby("ProductCategory")["Revenue"].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(x=revenue_by_cat.index, y=revenue_by_cat.values, hue=revenue_by_cat.index,
            palette="viridis", legend=False)
plt.title("Total Revenue by Product Category", fontsize=13, fontweight="bold")
plt.xlabel("Product Category")
plt.ylabel("Total Revenue (Rs.)")
for i, v in enumerate(revenue_by_cat.values):
    plt.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("charts/01_bar_revenue_by_category.png")
plt.close()

# -----------------------------------------------------------------
# 2. LINE CHART - Monthly Revenue Trend
# -----------------------------------------------------------------
monthly_revenue = df.groupby("OrderMonth")["Revenue"].sum().sort_index()

plt.figure(figsize=(9, 5))
plt.plot(monthly_revenue.index, monthly_revenue.values, marker="o", color="#2a6f97", linewidth=2)
plt.title("Monthly Revenue Trend (2024)", fontsize=13, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Total Revenue (Rs.)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/02_line_monthly_revenue.png")
plt.close()

# -----------------------------------------------------------------
# 3. HISTOGRAM - Distribution of Customer Age
# -----------------------------------------------------------------
plt.figure(figsize=(8, 5))
sns.histplot(df["Age"], bins=20, kde=True, color="#e07a5f")
plt.title("Distribution of Customer Age", fontsize=13, fontweight="bold")
plt.xlabel("Age (years)")
plt.ylabel("Number of Orders")
plt.tight_layout()
plt.savefig("charts/03_histogram_age_distribution.png")
plt.close()

# -----------------------------------------------------------------
# 4. BOXPLOT - Price Distribution by Product Category (post-cleaning)
# -----------------------------------------------------------------
plt.figure(figsize=(9, 5))
sns.boxplot(data=df, x="ProductCategory", y="Price", hue="ProductCategory",
            palette="Set2", legend=False)
plt.title("Price Distribution by Product Category (After Outlier Handling)", fontsize=13, fontweight="bold")
plt.xlabel("Product Category")
plt.ylabel("Price (Rs.)")
plt.tight_layout()
plt.savefig("charts/04_boxplot_price_by_category.png")
plt.close()

# -----------------------------------------------------------------
# 5. SCATTER PLOT - Age vs Revenue
# -----------------------------------------------------------------
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="Age", y="Revenue", hue="ProductCategory",
                 palette="tab10", alpha=0.7, s=45)
plt.title("Customer Age vs Order Revenue", fontsize=13, fontweight="bold")
plt.xlabel("Age (years)")
plt.ylabel("Revenue (Rs.)")
plt.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("charts/05_scatter_age_vs_revenue.png")
plt.close()

# -----------------------------------------------------------------
# 6. HEATMAP - Correlation Between Numeric Columns
# -----------------------------------------------------------------
numeric_cols = ["Age", "Price", "Quantity", "Rating", "Revenue"]
corr = df[numeric_cols].corr()

plt.figure(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True, cbar_kws={"shrink": 0.8})
plt.title("Correlation Heatmap of Numeric Features", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("charts/06_heatmap_correlation.png")
plt.close()

# -----------------------------------------------------------------
# 7. BAR CHART - Number of Orders by Region
# -----------------------------------------------------------------
orders_by_region = df["Region"].value_counts()

plt.figure(figsize=(7, 5))
sns.barplot(x=orders_by_region.index, y=orders_by_region.values, hue=orders_by_region.index,
            palette="crest", legend=False)
plt.title("Number of Orders by Region", fontsize=13, fontweight="bold")
plt.xlabel("Region")
plt.ylabel("Number of Orders")
for i, v in enumerate(orders_by_region.values):
    plt.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("charts/07_bar_orders_by_region.png")
plt.close()

print("All 7 charts saved inside the 'charts' folder.")

# -----------------------------------------------------------------
# Print the numbers behind each chart, for reference in the README
# -----------------------------------------------------------------
print("\nRevenue by category:\n", revenue_by_cat)
print("\nMonthly revenue:\n", monthly_revenue)
print("\nOrders by region:\n", orders_by_region)
print("\nCorrelation matrix:\n", corr.round(2))
print("\nAge stats:\n", df["Age"].describe())
print("\nTop category by avg rating:\n", df.groupby("ProductCategory")["Rating"].mean().sort_values(ascending=False))
