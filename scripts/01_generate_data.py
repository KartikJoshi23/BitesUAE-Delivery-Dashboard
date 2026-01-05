# =============================================================================
# BitesUAE - Synthetic Data Generator (FIXED VERSION)
# Project C: UAE Food Delivery CX & Operations Dashboard
# Run this in Google Colab to generate Dataset.xlsx
# =============================================================================

# Step 1: Install required packages (run this cell first)
!pip install pandas numpy faker openpyxl --quiet

# =============================================================================
# Step 2: Import Libraries
# =============================================================================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import warnings
warnings.filterwarnings('ignore')

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

print("✅ Libraries imported successfully!")

# =============================================================================
# Step 3: Define Constants and Configurations
# =============================================================================

# Date ranges
TODAY = datetime.now().date()
ORDER_START_DATE = TODAY - timedelta(days=90)
ORDER_END_DATE = TODAY
CUSTOMER_SIGNUP_START = TODAY - timedelta(days=540)  # 18 months
JOIN_DATE_START = TODAY - timedelta(days=730)  # 2 years

# Row counts
NUM_CUSTOMERS = 10000
NUM_RESTAURANTS = 500
NUM_RIDERS = 300
NUM_ORDERS = 25000
NUM_ORDER_ITEMS = 50000
NUM_DELIVERY_EVENTS = 25000  # 1:1 with orders

# City distribution
CITIES = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman']
CITY_WEIGHTS = [0.50, 0.25, 0.18, 0.07]

# Zone mapping by city (25 zones total)
CITY_ZONES = {
    'Dubai': [
        'Marina', 'JBR', 'Downtown Dubai', 'Business Bay', 'DIFC',
        'JLT', 'Deira', 'Bur Dubai', 'Al Barsha', 'Jumeirah',
        'Dubai Silicon Oasis', 'International City', 'Palm Jumeirah'
    ],
    'Abu Dhabi': [
        'Corniche', 'Khalidiya', 'Al Reem Island', 'Yas Island',
        'Khalifa City', 'Tourist Club Area'
    ],
    'Sharjah': [
        'Al Nahda', 'Al Qasimia', 'Al Majaz', 'Sharjah City Centre'
    ],
    'Ajman': [
        'Al Nuaimia', 'Ajman Downtown'
    ]
}

# Cuisine types and weights
CUISINES = ['Indian', 'Asian', 'Western', 'Emirati', 'Healthy']
CUISINE_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]

# Restaurant tiers with AOV ranges
RESTAURANT_TIERS = {
    'QSR': {'weight': 0.40, 'aov_min': 30, 'aov_max': 60, 'prep_min': 8, 'prep_max': 15},
    'Casual Dining': {'weight': 0.35, 'aov_min': 60, 'aov_max': 120, 'prep_min': 15, 'prep_max': 25},
    'Premium': {'weight': 0.20, 'aov_min': 120, 'aov_max': 250, 'prep_min': 20, 'prep_max': 35},
    'Fine Dining': {'weight': 0.05, 'aov_min': 250, 'aov_max': 500, 'prep_min': 30, 'prep_max': 50}
}

# Order status distribution
ORDER_STATUSES = ['Delivered', 'Cancelled', 'In Progress']
ORDER_STATUS_WEIGHTS = [0.82, 0.12, 0.06]

# Cancellation reasons (for cancelled orders only)
CANCELLATION_REASONS = [
    'Customer Cancelled', 'Restaurant Busy', 'Rider Unavailable',
    'Item Unavailable', 'Payment Failed'
]
CANCELLATION_WEIGHTS = [0.35, 0.25, 0.20, 0.15, 0.05]

# Payment methods
PAYMENT_METHODS = ['Card', 'Wallet', 'Cash']
PAYMENT_WEIGHTS = [0.55, 0.30, 0.15]

# Delay reasons
DELAY_REASONS = [
    'Restaurant Prep Delay', 'High Traffic', 'Rider Delayed at Pickup',
    'Wrong Address', 'Weather'
]
DELAY_REASON_WEIGHTS = [0.35, 0.25, 0.20, 0.10, 0.10]

# Customer tiers and signup sources
CUSTOMER_TIERS = ['New', 'Regular', 'Loyal', 'VIP']
CUSTOMER_TIER_WEIGHTS = [0.35, 0.35, 0.20, 0.10]
SIGNUP_SOURCES = ['Organic', 'Social Media', 'Referral', 'Paid Ads']
SIGNUP_SOURCE_WEIGHTS = [0.30, 0.25, 0.25, 0.20]

# Vehicle types for riders
VEHICLE_TYPES = ['Bike', 'Motorcycle', 'Car']
VEHICLE_WEIGHTS = [0.50, 0.40, 0.10]

# Rider statuses
RIDER_STATUSES = ['Active', 'Inactive', 'On Leave']
RIDER_STATUS_WEIGHTS = [0.85, 0.10, 0.05]

# Promo codes
PROMO_CODES = ['SAVE10', 'WELCOME20', 'BITES15', 'FREESHIP', 'VIP25', 'WEEKEND10', None]
PROMO_WEIGHTS = [0.08, 0.05, 0.07, 0.10, 0.03, 0.07, 0.60]  # 60% no promo

print("✅ Constants defined!")

# =============================================================================
# Step 4: Helper Functions
# =============================================================================

def get_random_city():
    """Return a random city based on distribution."""
    return np.random.choice(CITIES, p=CITY_WEIGHTS)

def get_random_zone(city):
    """Return a random zone for a given city."""
    return random.choice(CITY_ZONES[city])

def get_random_datetime(start_date, end_date):
    """Generate random datetime between two dates."""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return datetime.combine(start_date + timedelta(days=random_days), 
                           datetime.min.time()) + timedelta(seconds=random_seconds)

def get_order_datetime(base_date):
    """Generate order datetime with peak hour distribution."""
    # Define hour probabilities for 24 hours (0-23)
    # Peak hours: 12-13 (Lunch 25%), 19-21 (Dinner 45%), others (30%)
    hour_probs = [
        0.01,  # 0 AM
        0.01,  # 1 AM
        0.01,  # 2 AM
        0.01,  # 3 AM
        0.01,  # 4 AM
        0.01,  # 5 AM
        0.01,  # 6 AM
        0.02,  # 7 AM
        0.02,  # 8 AM
        0.02,  # 9 AM
        0.02,  # 10 AM
        0.03,  # 11 AM
        0.125, # 12 PM - Lunch Peak
        0.125, # 1 PM - Lunch Peak
        0.02,  # 2 PM
        0.02,  # 3 PM
        0.02,  # 4 PM
        0.03,  # 5 PM
        0.05,  # 6 PM
        0.15,  # 7 PM - Dinner Peak
        0.15,  # 8 PM - Dinner Peak
        0.15,  # 9 PM - Dinner Peak
        0.03,  # 10 PM
        0.02   # 11 PM
    ]
    
    # Normalize to sum to 1
    hour_probs = np.array(hour_probs)
    hour_probs = hour_probs / hour_probs.sum()
    
    hour = np.random.choice(range(24), p=hour_probs)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute, second=second))

def is_peak_hour(dt):
    """Check if datetime is during peak hours."""
    hour = dt.hour
    return hour in [12, 13, 19, 20, 21]

def get_delivery_status(is_peak):
    """Get delivery timing status with higher delay probability during peak."""
    if is_peak:
        # Peak: On-time 58%, Late<15 25%, Late>15 17%
        return np.random.choice(['on_time', 'late_minor', 'late_major'], 
                                p=[0.58, 0.25, 0.17])
    else:
        # Off-peak: On-time 78%, Late<15 15%, Late>15 7%
        return np.random.choice(['on_time', 'late_minor', 'late_major'], 
                                p=[0.78, 0.15, 0.07])

print("✅ Helper functions defined!")

# =============================================================================
# Step 5: Generate CUSTOMERS Table
# =============================================================================

def generate_customers():
    """Generate CUSTOMERS table with 10,000 rows."""
    print("Generating CUSTOMERS table...")
    
    customers = []
    for i in range(NUM_CUSTOMERS):
        city = get_random_city()
        customers.append({
            'customer_id': f'CUST_{i+1:05d}',
            'customer_name': fake.name(),
            'city': city,
            'area': get_random_zone(city),
            'signup_date': get_random_datetime(CUSTOMER_SIGNUP_START, TODAY).date(),
            'signup_source': np.random.choice(SIGNUP_SOURCES, p=SIGNUP_SOURCE_WEIGHTS),
            'customer_tier': np.random.choice(CUSTOMER_TIERS, p=CUSTOMER_TIER_WEIGHTS)
        })
    
    df = pd.DataFrame(customers)
    print(f"  ✅ Generated {len(df)} customers")
    return df

# =============================================================================
# Step 6: Generate RESTAURANTS Table
# =============================================================================

def generate_restaurants():
    """Generate RESTAURANTS table with 500 rows."""
    print("Generating RESTAURANTS table...")
    
    # Restaurant name prefixes and suffixes for UAE context
    prefixes = ['Al', 'The', 'Royal', 'Golden', 'Silver', 'Grand', 'Little', 'Big', 'New', 'Old']
    name_parts = ['Spice', 'Flame', 'Garden', 'Kitchen', 'House', 'Palace', 'Corner', 'Cafe', 'Bistro', 'Grill']
    suffixes = ['Express', 'Hub', 'Spot', 'Place', 'Junction', 'Point', 'Stop', 'Zone', '', '']
    
    tier_list = list(RESTAURANT_TIERS.keys())
    tier_weights = [RESTAURANT_TIERS[t]['weight'] for t in tier_list]
    
    restaurants = []
    for i in range(NUM_RESTAURANTS):
        city = get_random_city()
        tier = np.random.choice(tier_list, p=tier_weights)
        tier_config = RESTAURANT_TIERS[tier]
        
        # Generate restaurant name
        name = f"{random.choice(prefixes)} {random.choice(name_parts)} {random.choice(suffixes)}".strip()
        
        restaurants.append({
            'restaurant_id': f'REST_{i+1:03d}',
            'restaurant_name': name,
            'city': city,
            'zone': get_random_zone(city),
            'cuisine_type': np.random.choice(CUISINES, p=CUISINE_WEIGHTS),
            'restaurant_tier': tier,
            'avg_prep_time_mins': random.randint(tier_config['prep_min'], tier_config['prep_max']),
            'rating': round(random.uniform(3.0, 5.0), 1)
        })
    
    df = pd.DataFrame(restaurants)
    print(f"  ✅ Generated {len(df)} restaurants")
    return df

# =============================================================================
# Step 7: Generate RIDERS Table
# =============================================================================

def generate_riders():
    """Generate RIDERS table with 300 rows."""
    print("Generating RIDERS table...")
    
    riders = []
    for i in range(NUM_RIDERS):
        city = get_random_city()
        riders.append({
            'rider_id': f'RDR_{i+1:03d}',
            'rider_name': fake.name_male(),  # Most riders are male in UAE
            'city': city,
            'zone': get_random_zone(city),
            'vehicle_type': np.random.choice(VEHICLE_TYPES, p=VEHICLE_WEIGHTS),
            'rider_status': np.random.choice(RIDER_STATUSES, p=RIDER_STATUS_WEIGHTS),
            'join_date': get_random_datetime(JOIN_DATE_START, TODAY).date()
        })
    
    df = pd.DataFrame(riders)
    print(f"  ✅ Generated {len(df)} riders")
    return df

# =============================================================================
# Step 8: Generate ORDERS Table
# =============================================================================

def generate_orders(customers_df, restaurants_df):
    """Generate ORDERS table with 25,000 rows."""
    print("Generating ORDERS table...")
    
    customer_ids = customers_df['customer_id'].tolist()
    restaurant_ids = restaurants_df['restaurant_id'].tolist()
    
    # Create restaurant lookup for tier-based AOV
    restaurant_tier_lookup = restaurants_df.set_index('restaurant_id')['restaurant_tier'].to_dict()
    
    orders = []
    for i in range(NUM_ORDERS):
        restaurant_id = random.choice(restaurant_ids)
        tier = restaurant_tier_lookup[restaurant_id]
        tier_config = RESTAURANT_TIERS[tier]
        
        # Generate order datetime with peak distribution
        order_date = ORDER_START_DATE + timedelta(days=random.randint(0, 90))
        order_datetime = get_order_datetime(order_date)
        
        # Order status
        status = np.random.choice(ORDER_STATUSES, p=ORDER_STATUS_WEIGHTS)
        
        # Gross amount based on restaurant tier
        gross_amount = round(random.uniform(tier_config['aov_min'], tier_config['aov_max']), 2)
        
        # Promo code
        promo_code = np.random.choice(PROMO_CODES, p=PROMO_WEIGHTS)
        
        # Discount based on promo
        if promo_code:
            if 'FREESHIP' in str(promo_code):
                discount_amount = 0  # Free shipping handled separately
            elif '25' in str(promo_code):
                discount_amount = round(gross_amount * 0.25, 2)
            elif '20' in str(promo_code):
                discount_amount = round(gross_amount * 0.20, 2)
            elif '15' in str(promo_code):
                discount_amount = round(gross_amount * 0.15, 2)
            elif '10' in str(promo_code):
                discount_amount = round(gross_amount * 0.10, 2)
            else:
                discount_amount = round(gross_amount * random.uniform(0.05, 0.15), 2)
        else:
            discount_amount = 0
        
        net_amount = round(gross_amount - discount_amount, 2)
        
        # Delivery fee (0 for FREESHIP promo, else 5-15)
        if promo_code == 'FREESHIP':
            delivery_fee = 0
        else:
            delivery_fee = round(random.uniform(5, 15), 2)
        
        # Cancellation reason (only for cancelled orders)
        cancellation_reason = None
        if status == 'Cancelled':
            cancellation_reason = np.random.choice(CANCELLATION_REASONS, p=CANCELLATION_WEIGHTS)
        
        orders.append({
            'order_id': f'ORD_{i+1:05d}',
            'customer_id': random.choice(customer_ids),
            'restaurant_id': restaurant_id,
            'order_datetime': order_datetime,
            'order_status': status,
            'gross_amount': gross_amount,
            'discount_amount': discount_amount,
            'net_amount': net_amount,
            'delivery_fee': delivery_fee,
            'promo_code': promo_code,
            'payment_method': np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS),
            'cancellation_reason': cancellation_reason
        })
        
        # Progress indicator
        if (i + 1) % 5000 == 0:
            print(f"    Progress: {i+1}/{NUM_ORDERS} orders generated...")
    
    df = pd.DataFrame(orders)
    print(f"  ✅ Generated {len(df)} orders")
    return df

# =============================================================================
# Step 9: Generate ORDER_ITEMS Table
# =============================================================================

def generate_order_items(orders_df):
    """Generate ORDER_ITEMS table with ~50,000 rows (~2 per order)."""
    print("Generating ORDER_ITEMS table...")
    
    # Sample menu items by cuisine type
    MENU_ITEMS = {
        'Indian': ['Butter Chicken', 'Biryani', 'Naan', 'Samosa', 'Dal Makhani', 'Paneer Tikka', 'Mango Lassi', 'Gulab Jamun'],
        'Asian': ['Pad Thai', 'Sushi Roll', 'Dim Sum', 'Ramen', 'Fried Rice', 'Spring Rolls', 'Tom Yum Soup', 'Teriyaki Chicken'],
        'Western': ['Burger', 'Pizza', 'Pasta', 'Steak', 'Fish & Chips', 'Caesar Salad', 'Fries', 'Cheesecake'],
        'Emirati': ['Machboos', 'Harees', 'Luqaimat', 'Balaleet', 'Thareed', 'Madrooba', 'Karak Tea', 'Umm Ali'],
        'Healthy': ['Quinoa Bowl', 'Acai Bowl', 'Grilled Salmon', 'Green Smoothie', 'Avocado Toast', 'Greek Salad', 'Protein Shake', 'Veggie Wrap']
    }
    
    order_items = []
    item_counter = 0
    
    for idx, order in orders_df.iterrows():
        # Each order has 1-4 items (avg ~2)
        num_items = np.random.choice([1, 2, 2, 2, 3, 3, 4], p=[0.15, 0.30, 0.20, 0.15, 0.10, 0.05, 0.05])
        
        # Distribute gross_amount across items
        gross_amount = order['gross_amount']
        item_totals = np.random.dirichlet(np.ones(num_items)) * gross_amount
        
        for j in range(num_items):
            item_counter += 1
            quantity = random.randint(1, 3)
            item_total = round(item_totals[j], 2)
            unit_price = round(item_total / quantity, 2)
            
            # Recalculate to ensure consistency
            item_total = round(unit_price * quantity, 2)
            
            # Random menu item
            cuisine = random.choice(list(MENU_ITEMS.keys()))
            item_name = random.choice(MENU_ITEMS[cuisine])
            
            order_items.append({
                'item_id': f'ITM_{item_counter:05d}',
                'order_id': order['order_id'],
                'item_name': item_name,
                'quantity': quantity,
                'unit_price': unit_price,
                'item_total': item_total
            })
        
        # Progress indicator
        if (idx + 1) % 5000 == 0:
            print(f"    Progress: {idx+1}/{len(orders_df)} orders processed...")
    
    df = pd.DataFrame(order_items)
    print(f"  ✅ Generated {len(df)} order items")
    return df

# =============================================================================
# Step 10: Generate DELIVERY_EVENTS Table
# =============================================================================

def generate_delivery_events(orders_df, riders_df, restaurants_df):
    """Generate DELIVERY_EVENTS table with 25,000 rows (1:1 with orders)."""
    print("Generating DELIVERY_EVENTS table...")
    
    rider_ids = riders_df['rider_id'].tolist()
    restaurant_prep_lookup = restaurants_df.set_index('restaurant_id')['avg_prep_time_mins'].to_dict()
    
    events = []
    for idx, order in orders_df.iterrows():
        order_id = order['order_id']
        order_datetime = order['order_datetime']
        order_status = order['order_status']
        restaurant_id = order['restaurant_id']
        
        # Get restaurant's avg prep time
        avg_prep = restaurant_prep_lookup.get(restaurant_id, 20)
        
        # Order placed time = order_datetime
        order_placed_time = order_datetime
        
        # Restaurant confirmed (1-3 mins after order)
        restaurant_confirmed_time = order_placed_time + timedelta(minutes=random.randint(1, 3))
        
        # Actual prep time (varies around avg)
        actual_prep_mins = max(5, avg_prep + random.randint(-5, 10))
        food_ready_time = restaurant_confirmed_time + timedelta(minutes=actual_prep_mins)
        
        # Rider pickup (2-8 mins after food ready)
        rider_picked_up_time = food_ready_time + timedelta(minutes=random.randint(2, 8))
        
        # Determine if peak hour and delivery status
        is_peak = is_peak_hour(order_datetime)
        delivery_status = get_delivery_status(is_peak)
        
        # Estimated delivery time (typically 30-45 mins from order)
        estimated_mins = random.randint(30, 45)
        estimated_delivery_time = order_placed_time + timedelta(minutes=estimated_mins)
        
        # Initialize variables
        delivered_time = None
        actual_delivery_time_mins = None
        delay_reason = None
        
        # Actual delivery time based on status
        if order_status == 'Cancelled':
            delivered_time = None
            actual_delivery_time_mins = None
            delay_reason = None
        elif order_status == 'In Progress':
            delivered_time = None
            actual_delivery_time_mins = None
            delay_reason = None
        else:  # Delivered
            # Rider travel time (10-25 mins)
            base_travel_time = random.randint(10, 25)
            
            if delivery_status == 'on_time':
                # Ensure delivered before estimated
                delivered_time = rider_picked_up_time + timedelta(minutes=base_travel_time)
                # Adjust if would be late
                if delivered_time > estimated_delivery_time:
                    delivered_time = estimated_delivery_time - timedelta(minutes=random.randint(1, 5))
                delay_reason = None
                
            elif delivery_status == 'late_minor':
                # 1-15 mins late
                delay_mins = random.randint(1, 14)
                delivered_time = estimated_delivery_time + timedelta(minutes=delay_mins)
                delay_reason = np.random.choice(DELAY_REASONS, p=DELAY_REASON_WEIGHTS)
                
            else:  # late_major
                # 15-45 mins late
                delay_mins = random.randint(15, 45)
                delivered_time = estimated_delivery_time + timedelta(minutes=delay_mins)
                delay_reason = np.random.choice(DELAY_REASONS, p=DELAY_REASON_WEIGHTS)
            
            # Calculate actual delivery time in mins
            if delivered_time:
                actual_delivery_time_mins = round((delivered_time - order_placed_time).total_seconds() / 60, 2)
        
        events.append({
            'event_id': f'EVT_{idx+1:05d}',
            'order_id': order_id,
            'rider_id': random.choice(rider_ids),
            'order_placed_time': order_placed_time,
            'restaurant_confirmed_time': restaurant_confirmed_time,
            'food_ready_time': food_ready_time,
            'rider_picked_up_time': rider_picked_up_time,
            'delivered_time': delivered_time,
            'estimated_delivery_time': estimated_delivery_time,
            'actual_delivery_time_mins': actual_delivery_time_mins,
            'delay_reason': delay_reason
        })
        
        # Progress indicator
        if (idx + 1) % 5000 == 0:
            print(f"    Progress: {idx+1}/{len(orders_df)} events generated...")
    
    df = pd.DataFrame(events)
    print(f"  ✅ Generated {len(df)} delivery events")
    return df

# =============================================================================
# Step 11: Inject Data Quality Issues
# =============================================================================

def inject_data_quality_issues(customers, restaurants, riders, orders, order_items, delivery_events):
    """Inject all required data quality issues."""
    print("\n🔧 Injecting data quality issues...")
    
    # Make copies to avoid modifying original during iteration
    customers = customers.copy()
    restaurants = restaurants.copy()
    riders = riders.copy()
    orders = orders.copy()
    order_items = order_items.copy()
    delivery_events = delivery_events.copy()
    
    # ----- 1. MISSING VALUES -----
    print("  Adding missing values...")
    
    # Orders: ~100 missing discount_amount
    missing_discount_idx = random.sample(range(len(orders)), 100)
    orders.loc[missing_discount_idx, 'discount_amount'] = np.nan
    print(f"    - Orders: {len(missing_discount_idx)} missing discount_amount")
    
    # Delivery Events: ~50 missing delay_reason for late orders (additional to normal)
    late_orders_idx = delivery_events[delivery_events['delay_reason'].notna()].index.tolist()
    if len(late_orders_idx) >= 50:
        missing_delay_idx = random.sample(late_orders_idx, 50)
        delivery_events.loc[missing_delay_idx, 'delay_reason'] = np.nan
        print(f"    - Delivery Events: 50 missing delay_reason (for late orders)")
    
    # Riders: ~15 missing zone
    missing_zone_idx = random.sample(range(len(riders)), 15)
    riders.loc[missing_zone_idx, 'zone'] = np.nan
    print(f"    - Riders: {len(missing_zone_idx)} missing zone")
    
    # ----- 2. DUPLICATES -----
    print("  Adding duplicates...")
    
    # Orders: 100 duplicate order_id
    dup_orders = orders.sample(n=100)
    orders = pd.concat([orders, dup_orders], ignore_index=True)
    print(f"    - Orders: Added 100 duplicate rows")
    
    # Delivery Events: 80 duplicate event_id
    dup_events = delivery_events.sample(n=80)
    delivery_events = pd.concat([delivery_events, dup_events], ignore_index=True)
    print(f"    - Delivery Events: Added 80 duplicate rows")
    
    # Customers: 50 duplicate customer_id
    dup_customers = customers.sample(n=50)
    customers = pd.concat([customers, dup_customers], ignore_index=True)
    print(f"    - Customers: Added 50 duplicate rows")
    
    # ----- 3. INCONSISTENT LABELS -----
    print("  Adding inconsistent labels...")
    
    # City variations
    city_variations = {
        'Dubai': ['DUBAI', 'dubai', 'DXB'],
        'Abu Dhabi': ['ABU DHABI', 'abu dhabi', 'AUH'],
        'Sharjah': ['SHARJAH', 'sharjah', 'SHJ'],
        'Ajman': ['AJMAN', 'ajman', 'AJM']
    }
    
    for df in [customers, restaurants, riders]:
        inconsistent_idx = random.sample(range(len(df)), min(int(len(df) * 0.10), len(df)))
        for idx in inconsistent_idx:
            original = df.loc[idx, 'city']
            if pd.notna(original) and original in city_variations:
                df.loc[idx, 'city'] = random.choice(city_variations[original])
    print(f"    - Applied city variations (10% of rows)")
    
    # Cuisine variations
    cuisine_variations = {
        'Indian': ['indian', 'INDIAN', 'South Indian'],
        'Asian': ['asian', 'ASIAN', 'Pan-Asian'],
        'Western': ['western', 'WESTERN', 'Continental'],
        'Emirati': ['emirati', 'EMIRATI', 'Khaleeji'],
        'Healthy': ['healthy', 'HEALTHY', 'Health Food']
    }
    
    inconsistent_idx = random.sample(range(len(restaurants)), int(len(restaurants) * 0.12))
    for idx in inconsistent_idx:
        original = restaurants.loc[idx, 'cuisine_type']
        if pd.notna(original) and original in cuisine_variations:
            restaurants.loc[idx, 'cuisine_type'] = random.choice(cuisine_variations[original])
    print(f"    - Applied cuisine variations (12% of restaurants)")
    
    # Status variations
    status_variations = {
        'Delivered': ['delivered', 'DELIVERED', 'Complete'],
        'Cancelled': ['cancelled', 'CANCELLED', 'Canceled'],
        'In Progress': ['in progress', 'IN PROGRESS', 'Processing']
    }
    
    inconsistent_idx = random.sample(range(len(orders)), int(len(orders) * 0.08))
    for idx in inconsistent_idx:
        original = orders.loc[idx, 'order_status']
        if pd.notna(original) and original in status_variations:
            orders.loc[idx, 'order_status'] = random.choice(status_variations[original])
    print(f"    - Applied status variations (8% of orders)")
    
    # ----- 4. OUTLIERS -----
    print("  Adding outliers...")
    
    # Orders: 50 gross_amount > AED 1,500
    outlier_idx = random.sample(range(len(orders)), 50)
    for idx in outlier_idx:
        orders.loc[idx, 'gross_amount'] = round(random.uniform(1500, 3000), 2)
    print(f"    - Orders: 50 gross_amount outliers (>1500 AED)")
    
    # Delivery Events: 40 actual_delivery_time_mins > 120
    valid_delivery_idx = delivery_events[delivery_events['actual_delivery_time_mins'].notna()].index.tolist()
    if len(valid_delivery_idx) >= 40:
        outlier_idx = random.sample(valid_delivery_idx, 40)
        for idx in outlier_idx:
            delivery_events.loc[idx, 'actual_delivery_time_mins'] = round(random.uniform(121, 180), 2)
    print(f"    - Delivery Events: 40 delivery time outliers (>120 mins)")
    
    # Restaurants: 20 avg_prep_time_mins > 60
    outlier_idx = random.sample(range(len(restaurants)), 20)
    for idx in outlier_idx:
        restaurants.loc[idx, 'avg_prep_time_mins'] = random.randint(61, 90)
    print(f"    - Restaurants: 20 prep time outliers (>60 mins)")
    
    # ----- 5. IMPOSSIBLE VALUES -----
    print("  Adding impossible values...")
    
    # Orders: 20 delivered_time < order_placed_time
    delivered_idx = delivery_events[delivery_events['delivered_time'].notna()].index.tolist()
    if len(delivered_idx) >= 20:
        impossible_idx = random.sample(delivered_idx, 20)
        for idx in impossible_idx:
            order_placed = delivery_events.loc[idx, 'order_placed_time']
            # Make delivered_time 30-60 mins BEFORE order_placed_time
            delivery_events.loc[idx, 'delivered_time'] = order_placed - timedelta(minutes=random.randint(30, 60))
    print(f"    - Delivery Events: 20 impossible timestamps (delivered < placed)")
    
    # Delivery Events: 15 negative actual_delivery_time_mins
    if len(valid_delivery_idx) >= 15:
        negative_idx = random.sample(valid_delivery_idx, 15)
        for idx in negative_idx:
            delivery_events.loc[idx, 'actual_delivery_time_mins'] = random.randint(-60, -1)
    print(f"    - Delivery Events: 15 negative delivery times")
    
    # Orders: 10 discount_amount > gross_amount
    valid_orders_idx = orders[orders['discount_amount'].notna()].index.tolist()
    if len(valid_orders_idx) >= 10:
        impossible_discount_idx = random.sample(valid_orders_idx, 10)
        for idx in impossible_discount_idx:
            gross = orders.loc[idx, 'gross_amount']
            orders.loc[idx, 'discount_amount'] = round(gross * random.uniform(1.1, 1.5), 2)
    print(f"    - Orders: 10 discount > gross amount")
    
    # Shuffle all dataframes to mix in the issues
    customers = customers.sample(frac=1).reset_index(drop=True)
    restaurants = restaurants.sample(frac=1).reset_index(drop=True)
    riders = riders.sample(frac=1).reset_index(drop=True)
    orders = orders.sample(frac=1).reset_index(drop=True)
    order_items = order_items.sample(frac=1).reset_index(drop=True)
    delivery_events = delivery_events.sample(frac=1).reset_index(drop=True)
    
    print("✅ Data quality issues injected successfully!")
    
    return customers, restaurants, riders, orders, order_items, delivery_events

# =============================================================================
# Step 12: Main Execution - Generate All Data
# =============================================================================

print("\n" + "="*60)
print("🚀 STARTING DATA GENERATION")
print("="*60 + "\n")

# Generate base tables (clean data)
customers_df = generate_customers()
restaurants_df = generate_restaurants()
riders_df = generate_riders()
orders_df = generate_orders(customers_df, restaurants_df)
order_items_df = generate_order_items(orders_df)
delivery_events_df = generate_delivery_events(orders_df, riders_df, restaurants_df)

# Inject data quality issues
customers_df, restaurants_df, riders_df, orders_df, order_items_df, delivery_events_df = \
    inject_data_quality_issues(
        customers_df, restaurants_df, riders_df, 
        orders_df, order_items_df, delivery_events_df
    )

print("\n" + "="*60)
print("📊 FINAL DATA SUMMARY")
print("="*60)
print(f"  CUSTOMERS:       {len(customers_df):,} rows")
print(f"  RESTAURANTS:     {len(restaurants_df):,} rows")
print(f"  RIDERS:          {len(riders_df):,} rows")
print(f"  ORDERS:          {len(orders_df):,} rows")
print(f"  ORDER_ITEMS:     {len(order_items_df):,} rows")
print(f"  DELIVERY_EVENTS: {len(delivery_events_df):,} rows")

# =============================================================================
# Step 13: Export to Excel
# =============================================================================

print("\n📁 Exporting to Excel file...")

# Create Excel writer
with pd.ExcelWriter('BitesUAE_Dataset.xlsx', engine='openpyxl') as writer:
    customers_df.to_excel(writer, sheet_name='CUSTOMERS', index=False)
    restaurants_df.to_excel(writer, sheet_name='RESTAURANTS', index=False)
    riders_df.to_excel(writer, sheet_name='RIDERS', index=False)
    orders_df.to_excel(writer, sheet_name='ORDERS', index=False)
    order_items_df.to_excel(writer, sheet_name='ORDER_ITEMS', index=False)
    delivery_events_df.to_excel(writer, sheet_name='DELIVERY_EVENTS', index=False)

print("✅ Excel file created: BitesUAE_Dataset.xlsx")

# =============================================================================
# Step 14: Download the file (Google Colab)
# =============================================================================

from google.colab import files
files.download('BitesUAE_Dataset.xlsx')

print("\n" + "="*60)
print("🎉 DATA GENERATION COMPLETE!")
print("="*60)
print("\nThe file 'BitesUAE_Dataset.xlsx' contains 6 sheets:")
print("  1. CUSTOMERS       - Customer master data")
print("  2. RESTAURANTS     - Restaurant master data")
print("  3. RIDERS          - Rider master data")
print("  4. ORDERS          - Order transactions")
print("  5. ORDER_ITEMS     - Order line items")
print("  6. DELIVERY_EVENTS - Delivery tracking data")
print("\n⚠️  Data quality issues have been injected as per spec.")
print("    Run the cleaning pipeline before analysis!")
