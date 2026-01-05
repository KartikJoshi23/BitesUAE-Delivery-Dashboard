# =============================================================================
# BitesUAE - Data Cleaning Pipeline
# Project C: UAE Food Delivery CX & Operations Dashboard
# Run this in Google Colab after generating the raw dataset
# =============================================================================

# Step 1: Install and Import Libraries
!pip install pandas numpy openpyxl --quiet

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("✅ Libraries imported!")

# =============================================================================
# Step 2: Load the Raw Dataset
# =============================================================================

# Upload the file first (or use the one already in Colab)
from google.colab import files
print("📁 Please upload 'BitesUAE_Dataset.xlsx'...")
uploaded = files.upload()

# Load all sheets
print("\n📊 Loading dataset...")
xlsx = pd.ExcelFile('BitesUAE_Dataset.xlsx')

customers_raw = pd.read_excel(xlsx, 'CUSTOMERS')
restaurants_raw = pd.read_excel(xlsx, 'RESTAURANTS')
riders_raw = pd.read_excel(xlsx, 'RIDERS')
orders_raw = pd.read_excel(xlsx, 'ORDERS')
order_items_raw = pd.read_excel(xlsx, 'ORDER_ITEMS')
delivery_events_raw = pd.read_excel(xlsx, 'DELIVERY_EVENTS')

print("✅ Dataset loaded successfully!")
print(f"\n📋 Raw Data Row Counts:")
print(f"   CUSTOMERS:       {len(customers_raw):,}")
print(f"   RESTAURANTS:     {len(restaurants_raw):,}")
print(f"   RIDERS:          {len(riders_raw):,}")
print(f"   ORDERS:          {len(orders_raw):,}")
print(f"   ORDER_ITEMS:     {len(order_items_raw):,}")
print(f"   DELIVERY_EVENTS: {len(delivery_events_raw):,}")

# =============================================================================
# Step 3: Data Quality Assessment (Before Cleaning)
# =============================================================================

print("\n" + "="*70)
print("🔍 DATA QUALITY ASSESSMENT - BEFORE CLEANING")
print("="*70)

def assess_quality(df, name, id_column):
    """Assess data quality issues in a dataframe."""
    print(f"\n📊 {name}:")
    
    # Duplicates
    duplicates = df[id_column].duplicated().sum()
    print(f"   • Duplicate {id_column}: {duplicates}")
    
    # Missing values
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if len(missing_cols) > 0:
        print(f"   • Missing values:")
        for col, count in missing_cols.items():
            print(f"      - {col}: {count}")
    else:
        print(f"   • Missing values: None")
    
    return duplicates

# Assess each table
dup_customers = assess_quality(customers_raw, "CUSTOMERS", "customer_id")
dup_restaurants = assess_quality(restaurants_raw, "RESTAURANTS", "restaurant_id")
dup_riders = assess_quality(riders_raw, "RIDERS", "rider_id")
dup_orders = assess_quality(orders_raw, "ORDERS", "order_id")
dup_items = assess_quality(order_items_raw, "ORDER_ITEMS", "item_id")
dup_events = assess_quality(delivery_events_raw, "DELIVERY_EVENTS", "event_id")

# Check inconsistent labels
print(f"\n📊 INCONSISTENT LABELS:")
print(f"   • Cities in CUSTOMERS: {customers_raw['city'].unique().tolist()}")
print(f"   • Cuisines in RESTAURANTS: {restaurants_raw['cuisine_type'].unique().tolist()}")
print(f"   • Order Statuses: {orders_raw['order_status'].unique().tolist()}")

# Check outliers
print(f"\n📊 POTENTIAL OUTLIERS:")
print(f"   • Orders with gross_amount > 1500: {len(orders_raw[orders_raw['gross_amount'] > 1500])}")
print(f"   • Deliveries with time > 120 mins: {len(delivery_events_raw[delivery_events_raw['actual_delivery_time_mins'] > 120])}")
print(f"   • Restaurants with prep_time > 60: {len(restaurants_raw[restaurants_raw['avg_prep_time_mins'] > 60])}")

# Check impossible values
print(f"\n📊 IMPOSSIBLE VALUES:")
# Negative delivery times
negative_times = delivery_events_raw[delivery_events_raw['actual_delivery_time_mins'] < 0]
print(f"   • Negative delivery times: {len(negative_times)}")

# Discount > Gross
invalid_discounts = orders_raw[orders_raw['discount_amount'] > orders_raw['gross_amount']]
print(f"   • Discount > Gross amount: {len(invalid_discounts)}")

# Delivered before ordered
delivery_events_raw['order_placed_time'] = pd.to_datetime(delivery_events_raw['order_placed_time'])
delivery_events_raw['delivered_time'] = pd.to_datetime(delivery_events_raw['delivered_time'])
impossible_times = delivery_events_raw[
    delivery_events_raw['delivered_time'].notna() & 
    (delivery_events_raw['delivered_time'] < delivery_events_raw['order_placed_time'])
]
print(f"   • Delivered before ordered: {len(impossible_times)}")

# =============================================================================
# Step 4: Create Cleaning Functions
# =============================================================================

print("\n" + "="*70)
print("🧹 STARTING DATA CLEANING")
print("="*70)

# ---- Standardization Mappings ----
CITY_MAPPING = {
    'dubai': 'Dubai', 'DUBAI': 'Dubai', 'DXB': 'Dubai',
    'abu dhabi': 'Abu Dhabi', 'ABU DHABI': 'Abu Dhabi', 'AUH': 'Abu Dhabi',
    'sharjah': 'Sharjah', 'SHARJAH': 'Sharjah', 'SHJ': 'Sharjah',
    'ajman': 'Ajman', 'AJMAN': 'Ajman', 'AJM': 'Ajman'
}

CUISINE_MAPPING = {
    'indian': 'Indian', 'INDIAN': 'Indian', 'South Indian': 'Indian',
    'asian': 'Asian', 'ASIAN': 'Asian', 'Pan-Asian': 'Asian',
    'western': 'Western', 'WESTERN': 'Western', 'Continental': 'Western',
    'emirati': 'Emirati', 'EMIRATI': 'Emirati', 'Khaleeji': 'Emirati',
    'healthy': 'Healthy', 'HEALTHY': 'Healthy', 'Health Food': 'Healthy'
}

STATUS_MAPPING = {
    'delivered': 'Delivered', 'DELIVERED': 'Delivered', 'Complete': 'Delivered',
    'cancelled': 'Cancelled', 'CANCELLED': 'Cancelled', 'Canceled': 'Cancelled',
    'in progress': 'In Progress', 'IN PROGRESS': 'In Progress', 'Processing': 'In Progress'
}

TIER_MAPPING = {
    'new': 'New', 'NEW': 'New',
    'regular': 'Regular', 'REGULAR': 'Regular',
    'loyal': 'Loyal', 'LOYAL': 'Loyal',
    'vip': 'VIP', 'Vip': 'VIP'
}

def standardize_column(df, column, mapping):
    """Standardize values in a column using a mapping dictionary."""
    df[column] = df[column].replace(mapping)
    return df

def remove_duplicates(df, id_column, name):
    """Remove duplicate rows based on ID column."""
    before = len(df)
    df = df.drop_duplicates(subset=[id_column], keep='first')
    after = len(df)
    print(f"   ✓ {name}: Removed {before - after} duplicates")
    return df

# =============================================================================
# Step 5: Clean CUSTOMERS Table
# =============================================================================

print("\n🧹 Cleaning CUSTOMERS...")
customers = customers_raw.copy()

# 1. Remove duplicates
customers = remove_duplicates(customers, 'customer_id', 'CUSTOMERS')

# 2. Standardize city names
customers = standardize_column(customers, 'city', CITY_MAPPING)
print(f"   ✓ Standardized city names")

# 3. Standardize customer tier (if any variations)
customers = standardize_column(customers, 'customer_tier', TIER_MAPPING)
print(f"   ✓ Standardized customer tiers")

# 4. Validate signup_date (should not be in future)
today = pd.Timestamp.now().date()
future_dates = customers['signup_date'] > pd.Timestamp(today)
if future_dates.any():
    customers.loc[future_dates, 'signup_date'] = today
    print(f"   ✓ Fixed {future_dates.sum()} future signup dates")

print(f"   ✅ CUSTOMERS cleaned: {len(customers)} rows")

# =============================================================================
# Step 6: Clean RESTAURANTS Table
# =============================================================================

print("\n🧹 Cleaning RESTAURANTS...")
restaurants = restaurants_raw.copy()

# 1. Remove duplicates
restaurants = remove_duplicates(restaurants, 'restaurant_id', 'RESTAURANTS')

# 2. Standardize city names
restaurants = standardize_column(restaurants, 'city', CITY_MAPPING)
print(f"   ✓ Standardized city names")

# 3. Standardize cuisine types
restaurants = standardize_column(restaurants, 'cuisine_type', CUISINE_MAPPING)
print(f"   ✓ Standardized cuisine types")

# 4. Cap outlier prep times at 60 minutes
outlier_prep = restaurants['avg_prep_time_mins'] > 60
restaurants.loc[outlier_prep, 'avg_prep_time_mins'] = 60
print(f"   ✓ Capped {outlier_prep.sum()} outlier prep times to 60 mins")

# 5. Ensure rating is between 1-5
restaurants['rating'] = restaurants['rating'].clip(1.0, 5.0)
print(f"   ✓ Validated ratings (1-5 range)")

print(f"   ✅ RESTAURANTS cleaned: {len(restaurants)} rows")

# =============================================================================
# Step 7: Clean RIDERS Table
# =============================================================================

print("\n🧹 Cleaning RIDERS...")
riders = riders_raw.copy()

# 1. Remove duplicates
riders = remove_duplicates(riders, 'rider_id', 'RIDERS')

# 2. Standardize city names
riders = standardize_column(riders, 'city', CITY_MAPPING)
print(f"   ✓ Standardized city names")

# 3. Fill missing zones with 'Unknown'
missing_zones = riders['zone'].isna().sum()
riders['zone'] = riders['zone'].fillna('Unknown')
print(f"   ✓ Filled {missing_zones} missing zones with 'Unknown'")

print(f"   ✅ RIDERS cleaned: {len(riders)} rows")

# =============================================================================
# Step 8: Clean ORDERS Table
# =============================================================================

print("\n🧹 Cleaning ORDERS...")
orders = orders_raw.copy()

# 1. Remove duplicates
orders = remove_duplicates(orders, 'order_id', 'ORDERS')

# 2. Standardize order status
orders = standardize_column(orders, 'order_status', STATUS_MAPPING)
print(f"   ✓ Standardized order statuses")

# 3. Fix impossible discounts (discount > gross)
invalid_discount_mask = orders['discount_amount'] > orders['gross_amount']
# Set discount to 20% of gross for these cases
orders.loc[invalid_discount_mask, 'discount_amount'] = orders.loc[invalid_discount_mask, 'gross_amount'] * 0.20
print(f"   ✓ Fixed {invalid_discount_mask.sum()} invalid discounts")

# 4. Fill missing discount_amount with 0
missing_discounts = orders['discount_amount'].isna().sum()
orders['discount_amount'] = orders['discount_amount'].fillna(0)
print(f"   ✓ Filled {missing_discounts} missing discounts with 0")

# 5. Recalculate net_amount
orders['net_amount'] = orders['gross_amount'] - orders['discount_amount']
orders['net_amount'] = orders['net_amount'].round(2)
print(f"   ✓ Recalculated net_amount")

# 6. Cap gross_amount outliers at 1500 (99th percentile approach)
gross_cap = 1500
outlier_gross = orders['gross_amount'] > gross_cap
# For outliers, set to a reasonable max value
orders.loc[outlier_gross, 'gross_amount'] = orders.loc[~outlier_gross, 'gross_amount'].quantile(0.99)
orders.loc[outlier_gross, 'net_amount'] = orders.loc[outlier_gross, 'gross_amount'] - orders.loc[outlier_gross, 'discount_amount']
print(f"   ✓ Capped {outlier_gross.sum()} gross_amount outliers")

# 7. Clear cancellation_reason for non-cancelled orders
non_cancelled = orders['order_status'] != 'Cancelled'
orders.loc[non_cancelled, 'cancellation_reason'] = None
print(f"   ✓ Validated cancellation_reason field")

# 8. Ensure delivery_fee is non-negative
orders['delivery_fee'] = orders['delivery_fee'].clip(lower=0)
print(f"   ✓ Validated delivery fees")

print(f"   ✅ ORDERS cleaned: {len(orders)} rows")

# =============================================================================
# Step 9: Clean ORDER_ITEMS Table
# =============================================================================

print("\n🧹 Cleaning ORDER_ITEMS...")
order_items = order_items_raw.copy()

# 1. Remove duplicates
order_items = remove_duplicates(order_items, 'item_id', 'ORDER_ITEMS')

# 2. Remove orphan items (order_id not in orders)
valid_order_ids = set(orders['order_id'])
before = len(order_items)
order_items = order_items[order_items['order_id'].isin(valid_order_ids)]
print(f"   ✓ Removed {before - len(order_items)} orphan items")

# 3. Ensure quantity is positive
order_items['quantity'] = order_items['quantity'].clip(lower=1)
print(f"   ✓ Validated quantities")

# 4. Ensure unit_price is positive
order_items['unit_price'] = order_items['unit_price'].clip(lower=0.01)
print(f"   ✓ Validated unit prices")

# 5. Recalculate item_total
order_items['item_total'] = (order_items['unit_price'] * order_items['quantity']).round(2)
print(f"   ✓ Recalculated item_total")

print(f"   ✅ ORDER_ITEMS cleaned: {len(order_items)} rows")

# =============================================================================
# Step 10: Clean DELIVERY_EVENTS Table
# =============================================================================

print("\n🧹 Cleaning DELIVERY_EVENTS...")
delivery_events = delivery_events_raw.copy()

# 1. Remove duplicates
delivery_events = remove_duplicates(delivery_events, 'event_id', 'DELIVERY_EVENTS')

# 2. Remove orphan events (order_id not in orders)
before = len(delivery_events)
delivery_events = delivery_events[delivery_events['order_id'].isin(valid_order_ids)]
print(f"   ✓ Removed {before - len(delivery_events)} orphan events")

# 3. Convert datetime columns
datetime_cols = ['order_placed_time', 'restaurant_confirmed_time', 'food_ready_time', 
                 'rider_picked_up_time', 'delivered_time', 'estimated_delivery_time']
for col in datetime_cols:
    delivery_events[col] = pd.to_datetime(delivery_events[col], errors='coerce')

# 4. Fix impossible timestamps (delivered_time < order_placed_time)
impossible_mask = (
    delivery_events['delivered_time'].notna() & 
    (delivery_events['delivered_time'] < delivery_events['order_placed_time'])
)
# For these, recalculate delivered_time as order_placed + reasonable delivery time
for idx in delivery_events[impossible_mask].index:
    order_placed = delivery_events.loc[idx, 'order_placed_time']
    # Set delivered to 35-50 mins after order placed
    delivery_events.loc[idx, 'delivered_time'] = order_placed + timedelta(minutes=np.random.randint(35, 50))
print(f"   ✓ Fixed {impossible_mask.sum()} impossible timestamps")

# 5. Fix negative delivery times
negative_mask = delivery_events['actual_delivery_time_mins'] < 0
delivery_events.loc[negative_mask, 'actual_delivery_time_mins'] = np.nan
print(f"   ✓ Nullified {negative_mask.sum()} negative delivery times")

# 6. Recalculate actual_delivery_time_mins where possible
has_both_times = (
    delivery_events['delivered_time'].notna() & 
    delivery_events['order_placed_time'].notna()
)
delivery_events.loc[has_both_times, 'actual_delivery_time_mins'] = (
    (delivery_events.loc[has_both_times, 'delivered_time'] - 
     delivery_events.loc[has_both_times, 'order_placed_time']).dt.total_seconds() / 60
).round(2)
print(f"   ✓ Recalculated delivery times")

# 7. Cap outlier delivery times at 120 minutes
outlier_delivery = delivery_events['actual_delivery_time_mins'] > 120
delivery_events.loc[outlier_delivery, 'actual_delivery_time_mins'] = 120
print(f"   ✓ Capped {outlier_delivery.sum()} outlier delivery times")

# 8. Fill missing delay_reason for late deliveries
# First identify late deliveries
late_mask = (
    delivery_events['delivered_time'].notna() & 
    delivery_events['estimated_delivery_time'].notna() &
    (delivery_events['delivered_time'] > delivery_events['estimated_delivery_time']) &
    delivery_events['delay_reason'].isna()
)
delay_reasons = ['Restaurant Prep Delay', 'High Traffic', 'Rider Delayed at Pickup', 'Wrong Address', 'Weather']
delivery_events.loc[late_mask, 'delay_reason'] = np.random.choice(delay_reasons, size=late_mask.sum())
print(f"   ✓ Filled {late_mask.sum()} missing delay reasons for late deliveries")

# 9. Clear delay_reason for on-time deliveries
on_time_mask = (
    delivery_events['delivered_time'].notna() & 
    delivery_events['estimated_delivery_time'].notna() &
    (delivery_events['delivered_time'] <= delivery_events['estimated_delivery_time'])
)
delivery_events.loc[on_time_mask, 'delay_reason'] = None
print(f"   ✓ Validated delay_reason for on-time deliveries")

print(f"   ✅ DELIVERY_EVENTS cleaned: {len(delivery_events)} rows")

# =============================================================================
# Step 11: Add Calculated Columns for Analysis
# =============================================================================

print("\n📐 Adding calculated columns for analysis...")

# ---- ORDERS: Add time-based columns ----
orders['order_datetime'] = pd.to_datetime(orders['order_datetime'])
orders['order_date'] = orders['order_datetime'].dt.date
orders['order_hour'] = orders['order_datetime'].dt.hour
orders['order_day_of_week'] = orders['order_datetime'].dt.day_name()
orders['order_month'] = orders['order_datetime'].dt.to_period('M').astype(str)
orders['order_week'] = orders['order_datetime'].dt.to_period('W').astype(str)

# Is weekend flag
orders['is_weekend'] = orders['order_datetime'].dt.dayofweek.isin([4, 5])  # Friday, Saturday in UAE

# Peak hour flag (12-13, 19-21)
orders['is_peak_hour'] = orders['order_hour'].isin([12, 13, 19, 20, 21])

print("   ✓ Added time-based columns to ORDERS")

# ---- DELIVERY_EVENTS: Add performance columns ----
# Delivery performance category
def categorize_delivery(row):
    if pd.isna(row['delivered_time']):
        return 'Not Delivered'
    elif pd.isna(row['estimated_delivery_time']):
        return 'Unknown'
    elif row['delivered_time'] <= row['estimated_delivery_time']:
        return 'On Time'
    else:
        delay_mins = (row['delivered_time'] - row['estimated_delivery_time']).total_seconds() / 60
        if delay_mins <= 15:
            return 'Late (<15 min)'
        else:
            return 'Late (>15 min)'

delivery_events['delivery_performance'] = delivery_events.apply(categorize_delivery, axis=1)

# Delay minutes (if late)
delivery_events['delay_minutes'] = np.where(
    delivery_events['delivered_time'] > delivery_events['estimated_delivery_time'],
    (delivery_events['delivered_time'] - delivery_events['estimated_delivery_time']).dt.total_seconds() / 60,
    0
).round(2)

print("   ✓ Added performance columns to DELIVERY_EVENTS")

# ---- CUSTOMERS: Add tenure ----
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
customers['tenure_days'] = (pd.Timestamp.now() - customers['signup_date']).dt.days

print("   ✓ Added tenure column to CUSTOMERS")

# ---- RIDERS: Add tenure ----
riders['join_date'] = pd.to_datetime(riders['join_date'])
riders['tenure_days'] = (pd.Timestamp.now() - riders['join_date']).dt.days

print("   ✓ Added tenure column to RIDERS")

print("✅ Calculated columns added!")

# =============================================================================
# Step 12: Final Validation
# =============================================================================

print("\n" + "="*70)
print("✅ DATA QUALITY ASSESSMENT - AFTER CLEANING")
print("="*70)

print(f"\n📋 Final Row Counts:")
print(f"   CUSTOMERS:       {len(customers):,}")
print(f"   RESTAURANTS:     {len(restaurants):,}")
print(f"   RIDERS:          {len(riders):,}")
print(f"   ORDERS:          {len(orders):,}")
print(f"   ORDER_ITEMS:     {len(order_items):,}")
print(f"   DELIVERY_EVENTS: {len(delivery_events):,}")

print(f"\n📊 Validation Checks:")
print(f"   • Duplicate customer_id: {customers['customer_id'].duplicated().sum()}")
print(f"   • Duplicate restaurant_id: {restaurants['restaurant_id'].duplicated().sum()}")
print(f"   • Duplicate rider_id: {riders['rider_id'].duplicated().sum()}")
print(f"   • Duplicate order_id: {orders['order_id'].duplicated().sum()}")
print(f"   • Duplicate event_id: {delivery_events['event_id'].duplicated().sum()}")

print(f"\n📊 Standardized Values:")
print(f"   • Cities: {customers['city'].unique().tolist()}")
print(f"   • Cuisines: {restaurants['cuisine_type'].unique().tolist()}")
print(f"   • Order Statuses: {orders['order_status'].unique().tolist()}")

print(f"\n📊 Outliers Remaining:")
print(f"   • Orders with gross_amount > 1500: {len(orders[orders['gross_amount'] > 1500])}")
print(f"   • Deliveries with time > 120 mins: {len(delivery_events[delivery_events['actual_delivery_time_mins'] > 120])}")

print(f"\n📊 Impossible Values Remaining:")
print(f"   • Negative delivery times: {len(delivery_events[delivery_events['actual_delivery_time_mins'] < 0])}")
print(f"   • Discount > Gross: {len(orders[orders['discount_amount'] > orders['gross_amount']])}")

# =============================================================================
# Step 13: Export Cleaned Dataset
# =============================================================================

print("\n" + "="*70)
print("📁 EXPORTING CLEANED DATASET")
print("="*70)

# Export to Excel
with pd.ExcelWriter('BitesUAE_Cleaned.xlsx', engine='openpyxl') as writer:
    customers.to_excel(writer, sheet_name='CUSTOMERS', index=False)
    restaurants.to_excel(writer, sheet_name='RESTAURANTS', index=False)
    riders.to_excel(writer, sheet_name='RIDERS', index=False)
    orders.to_excel(writer, sheet_name='ORDERS', index=False)
    order_items.to_excel(writer, sheet_name='ORDER_ITEMS', index=False)
    delivery_events.to_excel(writer, sheet_name='DELIVERY_EVENTS', index=False)

print("✅ Exported: BitesUAE_Cleaned.xlsx")

# Also export as CSV files (useful for Power BI)
customers.to_csv('CUSTOMERS.csv', index=False)
restaurants.to_csv('RESTAURANTS.csv', index=False)
riders.to_csv('RIDERS.csv', index=False)
orders.to_csv('ORDERS.csv', index=False)
order_items.to_csv('ORDER_ITEMS.csv', index=False)
delivery_events.to_csv('DELIVERY_EVENTS.csv', index=False)

print("✅ Exported: Individual CSV files")

# Download files
from google.colab import files
files.download('BitesUAE_Cleaned.xlsx')

print("\n" + "="*70)
print("🎉 DATA CLEANING COMPLETE!")
print("="*70)

print("""
📁 Files Created:
   • BitesUAE_Cleaned.xlsx (all tables in one file)
   • Individual CSV files for each table

📊 Ready for Power BI:
   1. Open Power BI Desktop
   2. Get Data → Excel → Select BitesUAE_Cleaned.xlsx
   3. Load all 6 tables
   4. Set up relationships in Model view

🔗 Relationship Keys:
   • ORDERS.customer_id → CUSTOMERS.customer_id
   • ORDERS.restaurant_id → RESTAURANTS.restaurant_id
   • DELIVERY_EVENTS.order_id → ORDERS.order_id
   • DELIVERY_EVENTS.rider_id → RIDERS.rider_id
   • ORDER_ITEMS.order_id → ORDERS.order_id
""")
