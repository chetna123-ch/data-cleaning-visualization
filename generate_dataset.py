"""
generate_dataset.py
--------------------
Generates a realistic, intentionally MESSY raw dataset for an
"Online Retail Orders" data-cleaning & visualization project.

Run this file first (it writes raw_dataset.csv). It is provided so you
can see exactly how the raw data was created / regenerate it if needed.
You do NOT need to run this again if raw_dataset.csv is already present.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N = 500  # base number of unique orders

# ---------------------------------------------------------------
# Reference lists
# ---------------------------------------------------------------
categories = {
    "Electronics": ["Wireless Earbuds", "Smartphone", "Laptop", "Smartwatch", "Bluetooth Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Sweater"],
    "Grocery": ["Rice 5kg", "Olive Oil 1L", "Coffee Beans 500g", "Green Tea Box", "Almonds 250g"],
    "Furniture": ["Office Chair", "Study Table", "Bookshelf", "Bed Frame", "Sofa Set"],
    "Books": ["Fiction Novel", "Self-Help Book", "Cookbook", "Biography", "Comic Book"],
}
category_price_range = {
    "Electronics": (999, 45000),
    "Clothing": (299, 3500),
    "Grocery": (99, 1200),
    "Furniture": (1500, 25000),
    "Books": (150, 900),
}

regions = ["North", "South", "East", "West"]
genders = ["Male", "Female", "Other"]
payment_methods = ["Credit Card", "Debit Card", "UPI", "Cash on Delivery", "Net Banking"]
first_names = ["Aarav", "Vivaan", "Aditya", "Diya", "Saanvi", "Ananya", "Ishaan", "Kabir",
               "Riya", "Myra", "Arjun", "Sara", "Kavya", "Rohan", "Neha", "Aditi",
               "Manav", "Priya", "Karan", "Simran", "Yash", "Pooja", "Rahul", "Isha"]
last_names = ["Sharma", "Verma", "Patel", "Gupta", "Reddy", "Nair", "Iyer", "Singh",
              "Mehta", "Kapoor", "Joshi", "Chauhan", "Desai", "Malhotra", "Bhatt"]

rows = []
for i in range(1, N + 1):
    cat = np.random.choice(list(categories.keys()))
    product = np.random.choice(categories[cat])
    low, high = category_price_range[cat]
    price = round(np.random.uniform(low, high), 2)
    age = int(np.clip(np.random.normal(35, 12), 16, 70))
    qty = np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.12, 0.08, 0.06, 0.04])
    gender = np.random.choice(genders, p=[0.47, 0.47, 0.06])
    region = np.random.choice(regions)
    payment = np.random.choice(payment_methods)
    rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.08, 0.17, 0.35, 0.35])
    day = np.random.randint(1, 366)
    date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(day))
    name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"

    rows.append({
        "OrderID": 1000 + i,
        "CustomerName": name,
        "Age": age,
        "Gender": gender,
        "Region": region,
        "ProductCategory": cat,
        "Product": product,
        "Price": price,
        "Quantity": qty,
        "OrderDate": date,
        "PaymentMethod": payment,
        "Rating": rating,
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------
# 1) Inject inconsistent CASING / spacing in categorical columns
# ---------------------------------------------------------------
def messy_case(val):
    style = np.random.choice(["upper", "lower", "title", "pad"])
    if style == "upper":
        return val.upper()
    if style == "lower":
        return val.lower()
    if style == "pad":
        return f"  {val}  "
    return val

for col, frac in [("Gender", 0.25), ("Region", 0.25), ("ProductCategory", 0.20), ("PaymentMethod", 0.20)]:
    idx = df.sample(frac=frac, random_state=np.random.randint(10000)).index
    df.loc[idx, col] = df.loc[idx, col].apply(messy_case)

# Extra gender inconsistency: short codes
idx = df.sample(frac=0.10, random_state=1).index
df.loc[idx, "Gender"] = df.loc[idx, "Gender"].map({"Male": "M", "Female": "F", "Other": "O"}).fillna(df.loc[idx, "Gender"])

# ---------------------------------------------------------------
# 2) Price stored inconsistently (string with $ and commas) + wrong dtype
# ---------------------------------------------------------------
def messy_price(p):
    style = np.random.choice(["plain", "dollar", "comma"])
    if style == "dollar":
        return f"${p}"
    if style == "comma":
        return f"{p:,.2f}"
    return p

df["Price"] = df["Price"].astype(object)
idx = df.sample(frac=0.30, random_state=2).index
df.loc[idx, "Price"] = df.loc[idx, "Price"].apply(messy_price)

# ---------------------------------------------------------------
# 3) Quantity: some stored as text, a few invalid (0 / negative)
# ---------------------------------------------------------------
df["Quantity"] = df["Quantity"].astype(object)
idx = df.sample(frac=0.10, random_state=3).index
df.loc[idx, "Quantity"] = df.loc[idx, "Quantity"].astype(str)

idx_bad_qty = df.sample(n=6, random_state=4).index
df.loc[idx_bad_qty, "Quantity"] = np.random.choice([0, -1, -2], size=len(idx_bad_qty))

# ---------------------------------------------------------------
# 4) Age outliers / impossible values (data-entry errors)
# ---------------------------------------------------------------
idx_age_out = df.sample(n=8, random_state=5).index
df.loc[idx_age_out, "Age"] = np.random.choice([150, 200, -5, 0, 999], size=len(idx_age_out))

# ---------------------------------------------------------------
# 5) Price outliers (genuine extreme values, e.g. pricing errors)
# ---------------------------------------------------------------
idx_price_out = df.sample(n=7, random_state=6).index
df.loc[idx_price_out, "Price"] = [round(np.random.uniform(60000, 120000), 2) for _ in range(len(idx_price_out))]

# ---------------------------------------------------------------
# 6) Rating out-of-range values
# ---------------------------------------------------------------
idx_rating_bad = df.sample(n=5, random_state=7).index
df.loc[idx_rating_bad, "Rating"] = np.random.choice([0, 6, -1], size=len(idx_rating_bad))

# ---------------------------------------------------------------
# 7) OrderDate in mixed formats (string representations)
# ---------------------------------------------------------------
def messy_date(d):
    style = np.random.choice(["iso", "dmy", "text"])
    if style == "iso":
        return d.strftime("%Y-%m-%d")
    if style == "dmy":
        return d.strftime("%d/%m/%Y")
    return d.strftime("%b %d, %Y")

df["OrderDate"] = df["OrderDate"].apply(messy_date)

# ---------------------------------------------------------------
# 8) Inject MISSING values across several columns
# ---------------------------------------------------------------
def inject_missing(frame, col, frac, seed):
    idx = frame.sample(frac=frac, random_state=seed).index
    frame.loc[idx, col] = np.nan

inject_missing(df, "Age", 0.05, 11)
inject_missing(df, "Gender", 0.03, 12)
inject_missing(df, "Region", 0.03, 13)
inject_missing(df, "Price", 0.04, 14)
inject_missing(df, "Quantity", 0.02, 15)
inject_missing(df, "OrderDate", 0.03, 16)
inject_missing(df, "PaymentMethod", 0.04, 17)
inject_missing(df, "Rating", 0.10, 18)

# ---------------------------------------------------------------
# 9) Add DUPLICATE rows (exact copies of existing orders)
# ---------------------------------------------------------------
dupes = df.sample(n=25, random_state=20)
df = pd.concat([df, dupes], ignore_index=True)

# Shuffle final row order
df = df.sample(frac=1, random_state=99).reset_index(drop=True)

df.to_csv("raw_dataset.csv", index=False)
print(f"raw_dataset.csv created with {len(df)} rows and {df.shape[1]} columns.")
