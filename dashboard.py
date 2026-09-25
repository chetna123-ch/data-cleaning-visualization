"""
dashboard.py
------------
Interactive Streamlit dashboard for the cleaned retail-orders dataset.

Run with:
    streamlit run dashboard.py

(Requires: pip install streamlit pandas matplotlib seaborn)

In Google Colab, Streamlit needs a tunnel (e.g. pyngrok/localtunnel) to
be reachable, so this file is best run locally in VS Code / terminal.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_style("whitegrid")

st.set_page_config(page_title="Retail Orders Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_dataset.csv", parse_dates=["OrderDate"])
    return df


df = load_data()

st.title("Online Retail Orders Dashboard")
st.caption("Cleaned dataset generated for the Data Cleaning & Visualization project")

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Product Category", sorted(df["ProductCategory"].unique()),
    default=sorted(df["ProductCategory"].unique())
)
regions = st.sidebar.multiselect(
    "Region", sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

filtered = df[df["ProductCategory"].isin(categories) & df["Region"].isin(regions)]

# ---------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", f"{len(filtered):,}")
col2.metric("Total Revenue", f"Rs. {filtered['Revenue'].sum():,.0f}")
col3.metric("Avg Order Value", f"Rs. {filtered['Revenue'].mean():,.0f}" if len(filtered) else "-")
col4.metric("Avg Rating", f"{filtered['Rating'].mean():.2f} / 5" if len(filtered) else "-")

st.divider()

# ---------------------------------------------------------------
# Row 1: Bar chart + Line chart
# ---------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Revenue by Product Category")
    rev_cat = filtered.groupby("ProductCategory")["Revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(x=rev_cat.index, y=rev_cat.values, hue=rev_cat.index, palette="viridis", legend=False, ax=ax)
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Revenue (Rs.)")
    plt.xticks(rotation=30)
    st.pyplot(fig)

with c2:
    st.subheader("Monthly Revenue Trend")
    monthly = filtered.groupby("OrderMonth")["Revenue"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(monthly.index, monthly.values, marker="o", color="#2a6f97")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (Rs.)")
    plt.xticks(rotation=60)
    st.pyplot(fig)

# ---------------------------------------------------------------
# Row 2: Histogram + Boxplot
# ---------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Customer Age Distribution")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.histplot(filtered["Age"], bins=15, kde=True, color="#e07a5f", ax=ax)
    ax.set_xlabel("Age")
    st.pyplot(fig)

with c4:
    st.subheader("Price Spread by Category")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.boxplot(data=filtered, x="ProductCategory", y="Price", hue="ProductCategory",
                palette="Set2", legend=False, ax=ax)
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Price (Rs.)")
    plt.xticks(rotation=30)
    st.pyplot(fig)

# ---------------------------------------------------------------
# Row 3: Scatter + Heatmap
# ---------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.subheader("Age vs Revenue")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.scatterplot(data=filtered, x="Age", y="Revenue", hue="ProductCategory",
                     palette="tab10", alpha=0.7, ax=ax)
    st.pyplot(fig)

with c6:
    st.subheader("Correlation Heatmap")
    numeric_cols = ["Age", "Price", "Quantity", "Rating", "Revenue"]
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(filtered[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

st.divider()
st.subheader("Filtered Data")
st.dataframe(filtered.reset_index(drop=True))
