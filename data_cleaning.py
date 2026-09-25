"""
data_cleaning.py
-----------------
Loads raw_dataset.csv, explores it, cleans it using Pandas & NumPy,
and saves the result as cleaned_dataset.csv.

Run with:  python data_cleaning.py
"""

import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)

# =================================================================
# 1. LOAD THE RAW DATASET
# =================================================================
df = pd.read_csv("raw_dataset.csv")
print("=" * 60)
print("STEP 1: LOAD DATA")
print("=" * 60)
print(f"Raw dataset shape: {df.shape}")

# =================================================================
# 2. EXPLORE THE DATASET
# =================================================================
print("\n" + "=" * 60)
print("STEP 2: EXPLORE DATA")
print("=" * 60)
print("\nColumn data types:\n", df.dtypes)
print("\nFirst 5 rows:\n", df.head())
print("\nNumeric summary:\n", df.describe(include=[np.number]))

# =================================================================
# 3. IDENTIFY MISSING VALUES
# =================================================================
print("\n" + "=" * 60)
print("STEP 3: MISSING VALUES (before cleaning)")
print("=" * 60)
missing_before = df.isnull().sum()
print(missing_before[missing_before > 0])

# =================================================================
# 4. REMOVE DUPLICATE RECORDS
# =================================================================
print("\n" + "=" * 60)
print("STEP 4: DUPLICATES")
print("=" * 60)
n_dupes = df.duplicated().sum()
print(f"Exact duplicate rows found: {n_dupes}")
df = df.drop_duplicates().reset_index(drop=True)
print(f"Shape after removing duplicates: {df.shape}")

# =================================================================
# 5. STANDARDISE TEXT / CATEGORICAL COLUMNS
#    (fix inconsistent casing, stray whitespace, short codes)
# =================================================================
print("\n" + "=" * 60)
print("STEP 5: FIX INCONSISTENT CATEGORICAL VALUES")
print("=" * 60)

text_cols = ["Gender", "Region", "ProductCategory", "PaymentMethod", "CustomerName"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()

df["Region"] = df["Region"].str.title()
df["ProductCategory"] = df["ProductCategory"].str.title()

df["Gender"] = df["Gender"].str.upper().map(
    {"M": "Male", "MALE": "Male", "F": "Female", "FEMALE": "Female",
     "O": "Other", "OTHER": "Other"}
)

payment_map = {
    "CREDIT CARD": "Credit Card", "DEBIT CARD": "Debit Card",
    "UPI": "UPI", "NET BANKING": "Net Banking",
    "CASH ON DELIVERY": "Cash on Delivery",
}
df["PaymentMethod"] = df["PaymentMethod"].str.upper().map(payment_map)
print("Standardised Gender, Region, ProductCategory, PaymentMethod values.")
print("Gender values now:", sorted(df["Gender"].dropna().unique()))
print("Region values now:", sorted(df["Region"].dropna().unique()))
print("ProductCategory values now:", sorted(df["ProductCategory"].dropna().unique()))
print("PaymentMethod values now:", sorted(df["PaymentMethod"].dropna().unique()))

# Restore NaN where the original value was literally "nan" (from str conversion)
df[text_cols] = df[text_cols].replace("nan", np.nan)

# =================================================================
# 6. FIX DATA TYPES: Price, Quantity, OrderDate
# =================================================================
print("\n" + "=" * 60)
print("STEP 6: FIX DATA TYPES")
print("=" * 60)

# --- Price: strip "$" and "," then convert to float
df["Price"] = (
    df["Price"].astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
print("Converted Price to numeric (float).")

# --- Quantity: convert to numeric
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

# Invalid quantities (<= 0) are data-entry errors -> treat as missing
invalid_qty = (df["Quantity"] <= 0).sum()
df.loc[df["Quantity"] <= 0, "Quantity"] = np.nan
print(f"Marked {invalid_qty} invalid (zero/negative) Quantity values as missing.")

# --- OrderDate: the raw data mixes 3 different date formats
#     (YYYY-MM-DD, DD/MM/YYYY, "Mon DD, YYYY"). A single generic
#     parser can silently swap day/month, so each known format is
#     tried explicitly instead.
def parse_order_date(val):
    if pd.isna(val):
        return pd.NaT
    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except ValueError:
            continue
    return pd.NaT

df["OrderDate"] = df["OrderDate"].apply(parse_order_date)
print("Parsed OrderDate (3 mixed formats) into a proper datetime column.")

# =================================================================
# 7. FIX IMPOSSIBLE / OUT-OF-RANGE VALUES
# =================================================================
print("\n" + "=" * 60)
print("STEP 7: FIX IMPOSSIBLE VALUES")
print("=" * 60)

# Age must be a realistic shopper age (10-90); anything else is an entry error
bad_age = (~df["Age"].between(10, 90)).sum()
df.loc[~df["Age"].between(10, 90), "Age"] = np.nan
print(f"Marked {bad_age} impossible Age values (e.g. -5, 0, 150, 999) as missing.")

# Rating must be between 1 and 5
bad_rating = (~df["Rating"].between(1, 5)).sum()
df.loc[~df["Rating"].between(1, 5), "Rating"] = np.nan
print(f"Marked {bad_rating} out-of-range Rating values (e.g. 0, 6, -1) as missing.")

# =================================================================
# 8. HANDLE MISSING VALUES
# =================================================================
print("\n" + "=" * 60)
print("STEP 8: HANDLE MISSING VALUES")
print("=" * 60)

# Rows with a missing OrderDate can't be used in time-based analysis -> drop
before_rows = len(df)
df = df.dropna(subset=["OrderDate"]).reset_index(drop=True)
print(f"Dropped {before_rows - len(df)} rows with a missing OrderDate.")

# Numeric columns -> fill with median (robust to outliers)
for col in ["Age", "Quantity", "Rating"]:
    med = df[col].median()
    n_missing = df[col].isnull().sum()
    df[col] = df[col].fillna(med)
    print(f"Filled {n_missing} missing '{col}' values with median = {med}")

# Price -> fill with the median price of the same ProductCategory
price_missing = df["Price"].isnull().sum()
df["Price"] = df.groupby("ProductCategory")["Price"].transform(lambda s: s.fillna(s.median()))
print(f"Filled {price_missing} missing 'Price' values with each category's median price.")

# Categorical columns -> fill with the column's mode (most frequent value)
for col in ["Gender", "Region", "PaymentMethod"]:
    mode_val = df[col].mode()[0]
    n_missing = df[col].isnull().sum()
    df[col] = df[col].fillna(mode_val)
    print(f"Filled {n_missing} missing '{col}' values with mode = '{mode_val}'")

print(f"\nRemaining missing values after cleaning: {df.isnull().sum().sum()}")

# =================================================================
# 9. DETECT & HANDLE OUTLIERS (IQR method) ON Price
#    Price ranges genuinely differ a lot by category (e.g. Electronics
#    vs Grocery), so the IQR bounds are computed PER CATEGORY -- this
#    avoids wrongly flagging a normal laptop price as an "outlier"
#    just because groceries are cheaper.
# =================================================================
print("\n" + "=" * 60)
print("STEP 9: OUTLIER DETECTION (IQR method) ON PRICE, PER CATEGORY")
print("=" * 60)

def iqr_bounds(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

total_outliers = 0
for cat, group in df.groupby("ProductCategory"):
    low, high = iqr_bounds(group["Price"])
    mask = (df["ProductCategory"] == cat) & ((df["Price"] < low) | (df["Price"] > high))
    n = mask.sum()
    total_outliers += n
    print(f"{cat:12s} -> valid range [{low:8.2f}, {high:8.2f}]  outliers: {n}")
    df.loc[mask, "Price"] = df.loc[mask, "Price"].clip(lower=low, upper=high)

print(f"\nTotal Price outliers detected & capped: {total_outliers}")

# =================================================================
# 10. FINAL TYPE CLEAN-UP & DERIVED COLUMN
# =================================================================
print("\n" + "=" * 60)
print("STEP 10: FINAL TYPES & DERIVED COLUMN")
print("=" * 60)

df["Age"] = df["Age"].round().astype(int)
df["Quantity"] = df["Quantity"].round().astype(int)
df["Rating"] = df["Rating"].round().astype(int)
df["Price"] = df["Price"].round(2)
df["Revenue"] = (df["Price"] * df["Quantity"]).round(2)
df["OrderMonth"] = df["OrderDate"].dt.to_period("M").astype(str)

print("Added 'Revenue' (Price x Quantity) and 'OrderMonth' columns.")
print("\nFinal dtypes:\n", df.dtypes)

# =================================================================
# 11. FINAL CHECKS & SAVE
# =================================================================
print("\n" + "=" * 60)
print("STEP 11: FINAL CHECKS")
print("=" * 60)
print(f"Final shape: {df.shape}")
print(f"Remaining duplicates: {df.duplicated().sum()}")
print(f"Remaining missing values: {df.isnull().sum().sum()}")

df.to_csv("cleaned_dataset.csv", index=False)
print("\nSaved cleaned dataset to cleaned_dataset.csv")
