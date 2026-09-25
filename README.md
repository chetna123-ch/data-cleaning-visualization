# Data Cleaning & Visualization Project
### Dataset: Online Retail Orders (synthetically generated)

A complete, beginner-friendly data-cleaning and visualization project built
with Python, Pandas, NumPy, Matplotlib, Seaborn and Streamlit.

---

## 1. Project Structure

```
project/
├── raw_dataset.csv              # Messy raw data (525 rows, 12 columns)
├── cleaned_dataset.csv          # Cleaned data (485 rows, 14 columns)
├── generate_dataset.py          # Creates raw_dataset.csv
├── data_cleaning.py             # Cleans raw_dataset.csv -> cleaned_dataset.csv
├── visualization.py             # Creates all 7 individual charts (charts/*.png)
├── visual_report.py             # Combines key charts into one dashboard image
├── dashboard.py                 # Interactive Streamlit dashboard
├── requirements.txt
├── cleaning_log.txt             # Captured console output of the cleaning run
├── charts/
│   ├── 00_visual_report.png     # Combined static "visual report"
│   ├── 01_bar_revenue_by_category.png
│   ├── 02_line_monthly_revenue.png
│   ├── 03_histogram_age_distribution.png
│   ├── 04_boxplot_price_by_category.png
│   ├── 05_scatter_age_vs_revenue.png
│   ├── 06_heatmap_correlation.png
│   └── 07_bar_orders_by_region.png
└── README.md
```

## 2. How to Run

**VS Code / local machine**
```bash
pip install -r requirements.txt

python generate_dataset.py     # (optional - raw_dataset.csv is already included)
python data_cleaning.py        # cleans the data -> cleaned_dataset.csv
python visualization.py        # creates all charts in charts/
python visual_report.py        # creates the combined visual report image
streamlit run dashboard.py     # launches the interactive dashboard
```

**Google Colab**
- Upload `raw_dataset.csv`, `data_cleaning.py`, `visualization.py`, `visual_report.py`
  to the Colab file panel (or your Drive), then run each script's contents in a
  cell, e.g. `!python data_cleaning.py`. `%matplotlib inline` will display charts
  directly if you paste the plotting code into cells instead of saving to file.
- Streamlit does not display natively in Colab; it needs a tunnel such as
  `pyngrok`. It runs directly with no extra setup in VS Code / any local terminal.

---

## 3. The Raw Dataset

`raw_dataset.csv` — **525 rows x 12 columns** of simulated e-commerce orders
(OrderID, CustomerName, Age, Gender, Region, ProductCategory, Product, Price,
Quantity, OrderDate, PaymentMethod, Rating).

Deliberately included data-quality problems:
- **Missing values** in Age, Gender, Region, Price, Quantity, OrderDate,
  PaymentMethod and Rating.
- **25 exact duplicate rows.**
- **Inconsistent categorical text** — mixed casing and stray whitespace, e.g.
  `"Male"`, `"MALE"`, `"male"`, `"M"`, `"  Male  "`.
- **Inconsistent Price formatting** — plain numbers, `"$1,234.56"`, `"12,345.00"`
  all mixed in the same column (so it loads as text, not numbers).
- **Mixed OrderDate formats** — `2024-06-11`, `20/12/2024`, `Apr 10, 2024`.
- **Invalid values** — Quantity of `0` or negative, Age of `-5`, `0`, `150`,
  `200`, `999`, Rating outside the valid 1-5 scale.
- **Genuine outliers** — a handful of Price values far above the normal
  range for their category.

## 4. Data-Cleaning Summary (actual results from `cleaning_log.txt`)

| Step | Result |
|---|---|
| Starting shape | 525 rows x 12 columns |
| Exact duplicate rows removed | 25 |
| Categorical values standardised | Gender, Region, ProductCategory, PaymentMethod -> consistent casing (e.g. `Male`, `Female`, `Other`) |
| Price cleaned | `$`/`,` stripped, converted to numeric |
| Quantity cleaned | Converted to numeric; 6 invalid (<=0) values treated as missing |
| OrderDate parsed | 3 mixed formats parsed into real datetimes |
| Impossible Age values | 33 values outside 10-90 marked missing |
| Out-of-range Rating values | 55 values outside 1-5 marked missing |
| Rows dropped | 15 rows with a missing OrderDate (can't be used in time analysis) |
| Missing Age filled | 30 values -> median (34) |
| Missing Quantity filled | 15 values -> median (1) |
| Missing Rating filled | 52 values -> median (4) |
| Missing Price filled | 20 values -> median price of that product's category |
| Missing Gender filled | 14 values -> mode ("Female") |
| Missing Region filled | 15 values -> mode ("South") |
| Missing PaymentMethod filled | 18 values -> mode ("UPI") |
| Outlier detection method | IQR, computed **per product category** (Price ranges genuinely differ by category, e.g. Electronics vs Grocery) |
| Price outliers found & capped | 6 (winsorized to each category's IQR bounds, rows kept) |
| **Final cleaned shape** | **485 rows x 14 columns** (added `Revenue` = Price x Quantity, and `OrderMonth`) |
| Missing values remaining | 0 |
| Duplicates remaining | 0 |

Full step-by-step console output is saved in `cleaning_log.txt`.

---

## 5. Visualizations & What They Show

**01 - Bar Chart: Total Revenue by Product Category**
Electronics (Rs. 2,814,842) and Furniture (Rs. 1,888,449) generate far more
revenue than Clothing, Grocery or Books combined — driven by their much
higher per-item price, not order volume.

**02 - Line Chart: Monthly Revenue Trend (2024)**
Revenue fluctuates month to month with peaks in April and June and a dip in
February, rather than following a steady seasonal pattern in this simulated
year.

**03 - Histogram: Customer Age Distribution**
Customer age is right-skewed and centered in the late-20s to 30s (mean ≈
34, median 34), with most shoppers between 25 and 45.

**04 - Boxplot: Price Distribution by Category (after cleaning)**
Electronics and Furniture have both the highest median prices and the
widest spread; Books and Grocery are tightly clustered at low prices —
confirming the category-aware outlier handling preserved genuine
price variation instead of flattening it.

**05 - Scatter Plot: Age vs Revenue**
There is no visible relationship between a customer's age and how much
they spend per order (confirmed by the near-zero correlation in the
heatmap) — high-value orders come from all age groups.

**06 - Heatmap: Correlation Between Numeric Features**
Revenue correlates strongly with Price (**0.84**) and moderately with
Quantity (**0.26**), while Age and Rating show almost no linear
relationship with any other numeric field.

**07 - Bar Chart: Number of Orders by Region**
South leads with 155 orders, followed by North (119) and West (115), with
East lowest at 96 — a relatively even spread across all four regions.

---

## 6. Key Insights

1. **Electronics and Furniture drive revenue**, together contributing about
   92% of total revenue (Rs. 5,086,999) despite being only 2 of 5
   categories — because of high unit price, not high order volume.
2. **Price is the main revenue driver** (correlation of 0.84 with Revenue),
   far more than Quantity (0.26) — customers mostly buy 1-2 units per
   order regardless of category.
3. **Customer age does not predict spending behaviour** — age shows almost
   no correlation with Price, Quantity, Revenue or Rating in this dataset.
4. **Customer satisfaction is fairly consistent across categories**, with
   average ratings all clustered tightly between 3.89 and 4.07 out of 5
   (Clothing highest, Furniture/Electronics slightly lower).
5. **Orders are broadly balanced across regions** (96-155 orders each),
   with the South region seeing the most activity.
6. **Real-world messiness was successfully resolved**: 25 duplicates
   removed, 8 columns had missing values imputed with statistically sound
   methods (median/mode/category-aware median), impossible values (e.g.
   age of 999, rating of 6) were caught and corrected, and Price outliers
   were detected and capped using the IQR method — all without losing
   more than 7.6% of the original rows (525 -> 485).

---

## 7. Dashboard

`dashboard.py` is a Streamlit app with:
- Sidebar filters for Product Category and Region
- KPI cards (Total Orders, Total Revenue, Avg Order Value, Avg Rating)
- All 6 core charts (bar, line, histogram, boxplot, scatter, heatmap),
  updating live with the filters
- A browsable table of the filtered data

`charts/00_visual_report.png` is a static one-page version of the same
report (KPIs + 6 charts) for when you just want an image to share.
