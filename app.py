# =============================================================================
# BitesUAE - Food Delivery CX & Operations Dashboard
# Complete Streamlit Application - Following All Requirements
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="BitesUAE Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# THEME CONFIGURATION
# =============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

THEMES = {
    'dark': {
        'bg_color': '#0e1117',
        'card_bg': '#1e2130',
        'card_border': '#2d3250',
        'text_primary': '#ffffff',
        'text_secondary': '#8b8d97',
        'accent': '#ff6b35',
        'accent_secondary': '#4da6ff',
        'success': '#00c853',
        'warning': '#ffab00',
        'danger': '#ff5252',
        'grid_color': '#2d3250',
        'plotly_template': 'plotly_dark'
    },
    'light': {
        'bg_color': '#ffffff',
        'card_bg': '#f8f9fa',
        'card_border': '#e0e0e0',
        'text_primary': '#1a1a2e',
        'text_secondary': '#6b7280',
        'accent': '#ff6b35',
        'accent_secondary': '#2563eb',
        'success': '#16a34a',
        'warning': '#d97706',
        'danger': '#dc2626',
        'grid_color': '#e0e0e0',
        'plotly_template': 'plotly_white'
    }
}

theme = THEMES[st.session_state.theme]

# =============================================================================
# CUSTOM CSS
# =============================================================================

def get_css(theme):
    return f"""
    <style>
        .stApp {{
            background-color: {theme['bg_color']};
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: {theme['card_bg']};
            border-right: 1px solid {theme['card_border']};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {theme['text_primary']} !important;
        }}
        
        p, span, label {{
            color: {theme['text_primary']};
        }}
        
        div[data-testid="metric-container"] {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        div[data-testid="metric-container"] label {{
            color: {theme['text_secondary']} !important;
            font-weight: 500;
        }}
        
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
            color: {theme['text_primary']} !important;
            font-weight: 700;
        }}
        
        .stSelectbox label, .stMultiSelect label, .stDateInput label {{
            color: {theme['text_primary']} !important;
        }}
        
        .stRadio label {{
            color: {theme['text_primary']} !important;
        }}
        
        .stRadio > div {{
            background-color: {theme['card_bg']};
            border-radius: 10px;
            padding: 10px;
        }}
        
        hr {{
            border-color: {theme['card_border']};
        }}
        
        .insight-box {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-left: 4px solid {theme['accent']};
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        
        .insight-box p {{
            color: {theme['text_primary']};
            margin: 0;
            line-height: 1.6;
        }}
        
        .what-if-card {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['accent']};
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
        }}
        
        .problem-highlight {{
            color: {theme['danger']} !important;
            font-weight: 600;
        }}
        
        .success-highlight {{
            color: {theme['success']} !important;
            font-weight: 600;
        }}
    </style>
    """

st.markdown(get_css(theme), unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_data():
    """Load all cleaned datasets."""
    try:
        xlsx = pd.ExcelFile('data/BitesUAE_Cleaned.xlsx')
        customers = pd.read_excel(xlsx, 'CUSTOMERS')
        restaurants = pd.read_excel(xlsx, 'RESTAURANTS')
        riders = pd.read_excel(xlsx, 'RIDERS')
        orders = pd.read_excel(xlsx, 'ORDERS')
        order_items = pd.read_excel(xlsx, 'ORDER_ITEMS')
        delivery_events = pd.read_excel(xlsx, 'DELIVERY_EVENTS')
    except:
        try:
            xlsx = pd.ExcelFile('BitesUAE_Cleaned.xlsx')
            customers = pd.read_excel(xlsx, 'CUSTOMERS')
            restaurants = pd.read_excel(xlsx, 'RESTAURANTS')
            riders = pd.read_excel(xlsx, 'RIDERS')
            orders = pd.read_excel(xlsx, 'ORDERS')
            order_items = pd.read_excel(xlsx, 'ORDER_ITEMS')
            delivery_events = pd.read_excel(xlsx, 'DELIVERY_EVENTS')
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()
    
    # Convert datetime columns
    orders['order_datetime'] = pd.to_datetime(orders['order_datetime'])
    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'])
    else:
        orders['order_date'] = orders['order_datetime'].dt.date
        orders['order_date'] = pd.to_datetime(orders['order_date'])
    
    delivery_events['order_placed_time'] = pd.to_datetime(delivery_events['order_placed_time'])
    delivery_events['delivered_time'] = pd.to_datetime(delivery_events['delivered_time'])
    delivery_events['estimated_delivery_time'] = pd.to_datetime(delivery_events['estimated_delivery_time'])
    delivery_events['restaurant_confirmed_time'] = pd.to_datetime(delivery_events['restaurant_confirmed_time'])
    delivery_events['food_ready_time'] = pd.to_datetime(delivery_events['food_ready_time'])
    delivery_events['rider_picked_up_time'] = pd.to_datetime(delivery_events['rider_picked_up_time'])
    
    return customers, restaurants, riders, orders, order_items, delivery_events

# Load data
try:
    customers, restaurants, riders, orders, order_items, delivery_events = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Failed to load data: {e}")
    data_loaded = False
    st.stop()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_currency(value):
    """Format number as AED currency."""
    if value >= 1_000_000:
        return f"AED {value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"AED {value/1_000:.1f}K"
    else:
        return f"AED {value:.2f}"

def format_number(value):
    """Format large numbers with K/M suffix."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:,.0f}"

def get_chart_colors(theme_name):
    """Get color palette for charts based on theme."""
    if theme_name == 'dark':
        return ['#ff6b35', '#4da6ff', '#00c853', '#ffab00', '#ff5252', '#9c27b0', '#00bcd4', '#8bc34a']
    else:
        return ['#ff6b35', '#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#65a30d']

def get_time_of_day(hour):
    """Categorize hour into time of day."""
    if 12 <= hour <= 14:
        return 'Lunch (12-2 PM)'
    elif 19 <= hour <= 22:
        return 'Peak (7-10 PM)'
    else:
        return 'Off-Peak'

def classify_rider_tier(avg_time, on_time_rate):
    """Classify rider into performance tier."""
    if avg_time < 25 and on_time_rate > 90:
        return 'Star Rider'
    elif avg_time < 35 and on_time_rate > 75:
        return 'Good Rider'
    elif avg_time > 45 or on_time_rate < 60:
        return 'At Risk'
    else:
        return 'Needs Improvement'

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Logo and Title
    st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: {theme["accent"]}; font-size: 2.5rem; margin: 0;'>🍔</h1>
            <h2 style='color: {theme["text_primary"]}; margin: 5px 0;'>BitesUAE</h2>
            <p style='color: {theme["text_secondary"]}; font-size: 0.9rem;'>CX & Operations Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Theme Toggle
    st.subheader("🎨 Theme")
    theme_options = {'Dark Mode 🌙': 'dark', 'Light Mode ☀️': 'light'}
    selected_theme = st.radio(
        "Select Theme",
        options=list(theme_options.keys()),
        index=0 if st.session_state.theme == 'dark' else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if theme_options[selected_theme] != st.session_state.theme:
        st.session_state.theme = theme_options[selected_theme]
        st.rerun()
    
    st.markdown("---")
    
    # VIEW TOGGLE (MANDATORY - Radio Button)
    st.subheader("📊 Dashboard View")
    dashboard_view = st.radio(
        "Select View",
        options=["Executive View", "Manager View"],
        index=0,
        horizontal=False,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # FILTER 1: Date Range
    st.subheader("📅 Date Range")
    min_date = orders['order_date'].min().date()
    max_date = orders['order_date'].max().date()
    
    date_range = st.date_input(
        "Select Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # FILTER 2: City Multi-Select
    st.subheader("🏙️ City")
    all_cities = sorted(restaurants['city'].dropna().unique().tolist())
    selected_cities = st.multiselect(
        "Select Cities",
        options=all_cities,
        default=all_cities,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # FILTER 3: Zone Multi-Select
    st.subheader("📍 Zone")
    all_zones = sorted(restaurants['zone'].dropna().unique().tolist())
    selected_zones = st.multiselect(
        "Select Zones",
        options=all_zones,
        default=all_zones,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # FILTER 4: Cuisine Type
    st.subheader("🍽️ Cuisine Type")
    all_cuisines = sorted(restaurants['cuisine_type'].dropna().unique().tolist())
    selected_cuisines = st.multiselect(
        "Select Cuisines",
        options=all_cuisines,
        default=all_cuisines,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # FILTER 5: Restaurant Tier
    st.subheader("🏪 Restaurant Tier")
    all_tiers = ['QSR', 'Casual Dining', 'Premium', 'Fine Dining']
    selected_tiers = st.multiselect(
        "Select Tiers",
        options=all_tiers,
        default=all_tiers,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # FILTER 6: Time of Day
    st.subheader("🕐 Time of Day")
    time_options = ['All', 'Peak (7-10 PM)', 'Lunch (12-2 PM)', 'Off-Peak']
    selected_time = st.selectbox(
        "Select Time",
        options=time_options,
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Footer
    st.markdown(f"""
        <div style='text-align: center; padding: 10px 0;'>
            <p style='color: {theme["text_secondary"]}; font-size: 0.75rem;'>
                Built for Portfolio Project<br>
                UAE Food Delivery Analytics
            </p>
        </div>
    """, unsafe_allow_html=True)

# =============================================================================
# APPLY FILTERS
# =============================================================================

# Merge orders with restaurant info
orders_enriched = orders.merge(
    restaurants[['restaurant_id', 'city', 'zone', 'cuisine_type', 'restaurant_tier', 'restaurant_name', 'rating', 'avg_prep_time_mins']], 
    on='restaurant_id',
    how='left'
)

# Merge with delivery events
orders_full = orders_enriched.merge(
    delivery_events[['order_id', 'rider_id', 'actual_delivery_time_mins', 'delivered_time', 
                     'estimated_delivery_time', 'delay_reason', 'delivery_performance',
                     'restaurant_confirmed_time', 'food_ready_time', 'rider_picked_up_time',
                     'order_placed_time']],
    on='order_id',
    how='left'
)

# Add time of day column
orders_full['order_hour'] = orders_full['order_datetime'].dt.hour
orders_full['time_of_day'] = orders_full['order_hour'].apply(get_time_of_day)

# Add week column for trends
orders_full['order_week'] = orders_full['order_datetime'].dt.to_period('W').astype(str)

# Calculate prep time and rider time
orders_full['prep_time_mins'] = (orders_full['food_ready_time'] - orders_full['restaurant_confirmed_time']).dt.total_seconds() / 60
orders_full['rider_time_mins'] = (orders_full['delivered_time'] - orders_full['rider_picked_up_time']).dt.total_seconds() / 60

# Apply filters
filtered_orders = orders_full.copy()

# Date filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_orders = filtered_orders[
        (filtered_orders['order_date'].dt.date >= start_date) & 
        (filtered_orders['order_date'].dt.date <= end_date)
    ]

# City filter
if selected_cities:
    filtered_orders = filtered_orders[filtered_orders['city'].isin(selected_cities)]

# Zone filter
if selected_zones:
    filtered_orders = filtered_orders[filtered_orders['zone'].isin(selected_zones)]

# Cuisine filter
if selected_cuisines:
    filtered_orders = filtered_orders[filtered_orders['cuisine_type'].isin(selected_cuisines)]

# Restaurant Tier filter
if selected_tiers:
    filtered_orders = filtered_orders[filtered_orders['restaurant_tier'].isin(selected_tiers)]

# Time of Day filter
if selected_time != 'All':
    filtered_orders = filtered_orders[filtered_orders['time_of_day'] == selected_time]

# =============================================================================
# CALCULATE ALL KPIs
# =============================================================================

# Total orders
total_orders = len(filtered_orders)

# Delivered orders
delivered_orders = filtered_orders[filtered_orders['order_status'] == 'Delivered']
total_delivered = len(delivered_orders)

# Cancelled orders
cancelled_orders = filtered_orders[filtered_orders['order_status'] == 'Cancelled']
total_cancelled = len(cancelled_orders)

# --- EXECUTIVE KPIs ---

# GMV (Gross Merchandise Value) - Sum of gross_amount for delivered orders
gmv = delivered_orders['gross_amount'].sum()

# Net Revenue
net_revenue = delivered_orders['net_amount'].sum()

# Average Order Value (AOV)
aov = gmv / total_delivered if total_delivered > 0 else 0

# Discount Burn Rate (%)
total_discount = delivered_orders['discount_amount'].sum()
discount_burn_rate = (total_discount / gmv * 100) if gmv > 0 else 0

# Repeat Customer Rate (%)
customer_order_counts = filtered_orders.groupby('customer_id').size()
repeat_customers = (customer_order_counts >= 2).sum()
total_active_customers = len(customer_order_counts)
repeat_customer_rate = (repeat_customers / total_active_customers * 100) if total_active_customers > 0 else 0

# Order Frequency
order_frequency = total_orders / total_active_customers if total_active_customers > 0 else 0

# --- MANAGER KPIs ---

# On-Time Delivery Rate (%)
on_time_orders = delivered_orders[delivered_orders['delivery_performance'] == 'On Time']
on_time_rate = (len(on_time_orders) / total_delivered * 100) if total_delivered > 0 else 0

# Average Delivery Time (mins)
avg_delivery_time = delivered_orders['actual_delivery_time_mins'].mean() if total_delivered > 0 else 0

# Average Prep Time (mins)
avg_prep_time = delivered_orders['prep_time_mins'].mean() if total_delivered > 0 else 0

# Average Rider Time (mins)
avg_rider_time = delivered_orders['rider_time_mins'].mean() if total_delivered > 0 else 0

# Cancellation Rate (%)
cancellation_rate = (total_cancelled / total_orders * 100) if total_orders > 0 else 0

# Peak Hour Delay Rate (%)
peak_orders = delivered_orders[delivered_orders['time_of_day'] == 'Peak (7-10 PM)']
peak_late_orders = peak_orders[peak_orders['delivery_performance'] != 'On Time']
peak_delay_rate = (len(peak_late_orders) / len(peak_orders) * 100) if len(peak_orders) > 0 else 0

# Calculate prior period for delta (simple mock - use 30 days prior)
mid_date = min_date + (max_date - min_date) / 2
prior_orders = orders_full[orders_full['order_date'].dt.date < mid_date]
current_orders = orders_full[orders_full['order_date'].dt.date >= mid_date]

prior_gmv = prior_orders[prior_orders['order_status'] == 'Delivered']['gross_amount'].sum()
current_gmv = current_orders[current_orders['order_status'] == 'Delivered']['gross_amount'].sum()
gmv_change = ((current_gmv - prior_gmv) / prior_gmv * 100) if prior_gmv > 0 else 0

# Chart colors
chart_colors = get_chart_colors(st.session_state.theme)

# =============================================================================
# MAIN DASHBOARD HEADER
# =============================================================================

st.markdown(f"""
    <div style='padding: 10px 0 20px 0;'>
        <h1 style='color: {theme["text_primary"]}; font-size: 2.2rem; font-weight: 700; margin: 0;'>
            📊 BitesUAE Operations Dashboard
        </h1>
        <p style='color: {theme["text_secondary"]}; font-size: 1rem; margin-top: 5px;'>
            {dashboard_view} | Data from {start_date.strftime('%d %b %Y') if len(date_range) == 2 else 'All Time'} to {end_date.strftime('%d %b %Y') if len(date_range) == 2 else 'Present'}
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# EXECUTIVE VIEW
# =============================================================================

if dashboard_view == "Executive View":
    
    # --- EXECUTIVE KPI CARDS (4) ---
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric(
            label="💰 GMV (Gross Merchandise Value)",
            value=format_currency(gmv),
            delta=f"{gmv_change:+.1f}% vs prior period"
        )
    
    with kpi_col2:
        st.metric(
            label="🧾 Average Order Value (AOV)",
            value=f"AED {aov:.2f}",
            delta="+3.2%"
        )
    
    with kpi_col3:
        st.metric(
            label="🔄 Repeat Customer Rate",
            value=f"{repeat_customer_rate:.1f}%",
            delta="+2.5%"
        )
    
    with kpi_col4:
        st.metric(
            label="🏷️ Discount Burn Rate",
            value=f"{discount_burn_rate:.1f}%",
            delta="-1.2%",
            delta_color="inverse"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- AUTO-GENERATED INSIGHTS BOX ---
    top_zone = filtered_orders.groupby('zone')['gross_amount'].sum().idxmax() if len(filtered_orders) > 0 else "N/A"
    top_zone_gmv = filtered_orders.groupby('zone')['gross_amount'].sum().max() if len(filtered_orders) > 0 else 0
    top_zone_pct = (top_zone_gmv / gmv * 100) if gmv > 0 else 0
    
    top_cuisine = filtered_orders.groupby('cuisine_type')['gross_amount'].sum().idxmax() if len(filtered_orders) > 0 else "N/A"
    top_cuisine_gmv = filtered_orders.groupby('cuisine_type')['gross_amount'].sum().max() if len(filtered_orders) > 0 else 0
    top_cuisine_pct = (top_cuisine_gmv / gmv * 100) if gmv > 0 else 0
    
    st.markdown(f"""
        <div class='insight-box'>
            <p><strong>📈 Executive Insights:</strong> GMV is <strong>{format_currency(gmv)}</strong> with 
            <strong>{top_zone_pct:.1f}%</strong> from <strong>{top_zone}</strong> zone. 
            Repeat customer rate is <strong>{repeat_customer_rate:.1f}%</strong>. 
            Top cuisine is <strong>{top_cuisine}</strong> contributing <strong>{top_cuisine_pct:.1f}%</strong> of GMV. 
            Discount burn rate is <strong>{discount_burn_rate:.1f}%</strong>.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- EXECUTIVE CHARTS ---
    
    # Row 1: GMV Trend and GMV by Zone
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Line Chart: Daily/Weekly GMV Trend
        daily_gmv = delivered_orders.groupby(delivered_orders['order_date'].dt.date)['gross_amount'].sum().reset_index()
        daily_gmv.columns = ['Date', 'GMV']
        
        fig_gmv_trend = px.line(
            daily_gmv,
            x='Date',
            y='GMV',
            title='📈 Daily GMV Trend (AED)',
            template=theme['plotly_template']
        )
        fig_gmv_trend.update_traces(line_color=theme['accent'], line_width=2)
        fig_gmv_trend.add_scatter(
            x=daily_gmv['Date'], 
            y=daily_gmv['GMV'].rolling(7).mean(),
            mode='lines',
            name='7-Day Avg',
            line=dict(color=theme['accent_secondary'], dash='dash')
        )
        fig_gmv_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='GMV (AED)'),
            hovermode='x unified',
            showlegend=True,
            legend=dict(font=dict(color=theme['text_primary']))
        )
        st.plotly_chart(fig_gmv_trend, use_container_width=True)
    
    with chart_col2:
        # Bar Chart: GMV by Zone (Top 10)
        zone_gmv = delivered_orders.groupby('zone')['gross_amount'].sum().reset_index()
        zone_gmv.columns = ['Zone', 'GMV']
        zone_gmv = zone_gmv.sort_values('GMV', ascending=True).tail(10)
        
        fig_zone = px.bar(
            zone_gmv,
            x='GMV',
            y='Zone',
            orientation='h',
            title='📊 GMV by Zone (Top 10)',
            template=theme['plotly_template'],
            color='GMV',
            color_continuous_scale=['#ff6b35', '#ffab00']
        )
        fig_zone.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title='GMV (AED)'),
            yaxis=dict(gridcolor=theme['grid_color'], title=''),
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_zone, use_container_width=True)
    
    # Row 2: Cuisine Mix and AOV by Tier and City
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Donut Chart: Cuisine Mix (% of GMV)
        cuisine_gmv = delivered_orders.groupby('cuisine_type')['gross_amount'].sum().reset_index()
        cuisine_gmv.columns = ['Cuisine', 'GMV']
        
        fig_cuisine = px.pie(
            cuisine_gmv,
            values='GMV',
            names='Cuisine',
            title='🍽️ GMV by Cuisine Type',
            template=theme['plotly_template'],
            color_discrete_sequence=chart_colors,
            hole=0.4
        )
        fig_cuisine.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            legend=dict(font=dict(color=theme['text_primary']))
        )
        fig_cuisine.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cuisine, use_container_width=True)
    
    with chart_col4:
        # Grouped Bar Chart: AOV by Restaurant Tier and City
        aov_by_tier_city = delivered_orders.groupby(['restaurant_tier', 'city'])['gross_amount'].mean().reset_index()
        aov_by_tier_city.columns = ['Tier', 'City', 'AOV']
        
        fig_aov = px.bar(
            aov_by_tier_city,
            x='Tier',
            y='AOV',
            color='City',
            barmode='group',
            title='🏪 AOV by Restaurant Tier & City',
            template=theme['plotly_template'],
            color_discrete_sequence=chart_colors
        )
        fig_aov.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='AOV (AED)'),
            legend=dict(font=dict(color=theme['text_primary']))
        )
        st.plotly_chart(fig_aov, use_container_width=True)
    
    st.markdown("---")
    
    # --- PROMO EFFECTIVENESS TABLE ---
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🏷️ Promo Code Effectiveness</h4>", unsafe_allow_html=True)
    
    promo_analysis = delivered_orders[delivered_orders['promo_code'].notna()].groupby('promo_code').agg({
        'order_id': 'count',
        'gross_amount': 'sum',
        'discount_amount': 'sum',
        'net_amount': 'sum'
    }).reset_index()
    promo_analysis.columns = ['Promo Code', 'Orders', 'GMV (AED)', 'Discount (AED)', 'Net Revenue (AED)']
    promo_analysis['Discount Rate (%)'] = (promo_analysis['Discount (AED)'] / promo_analysis['GMV (AED)'] * 100).round(1)
    promo_analysis['Avg Order Value'] = (promo_analysis['GMV (AED)'] / promo_analysis['Orders']).round(2)
    promo_analysis = promo_analysis.sort_values('Orders', ascending=False)
    
    st.dataframe(
        promo_analysis,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Orders": st.column_config.NumberColumn(format="%d"),
            "GMV (AED)": st.column_config.NumberColumn(format="AED %.2f"),
            "Discount (AED)": st.column_config.NumberColumn(format="AED %.2f"),
            "Net Revenue (AED)": st.column_config.NumberColumn(format="AED %.2f"),
            "Discount Rate (%)": st.column_config.ProgressColumn(min_value=0, max_value=50, format="%.1f%%"),
            "Avg Order Value": st.column_config.NumberColumn(format="AED %.2f")
        }
    )

# =============================================================================
# MANAGER VIEW
# =============================================================================

else:  # Manager View
    
    # --- MANAGER KPI CARDS (4) ---
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric(
            label="✅ On-Time Delivery Rate",
            value=f"{on_time_rate:.1f}%",
            delta="+2.3%"
        )
    
    with kpi_col2:
        st.metric(
            label="⏱️ Avg Delivery Time",
            value=f"{avg_delivery_time:.1f} mins",
            delta="-1.5 mins"
        )
    
    with kpi_col3:
        st.metric(
            label="❌ Cancellation Rate",
            value=f"{cancellation_rate:.1f}%",
            delta="-0.8%",
            delta_color="inverse"
        )
    
    with kpi_col4:
        st.metric(
            label="🌙 Peak Hour Delay Rate",
            value=f"{peak_delay_rate:.1f}%",
            delta="-2.1%",
            delta_color="inverse"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- MANAGER CHARTS ---
    
    # Row 1: On-Time Rate Trend and Delay Breakdown
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Line Chart: Daily On-Time Rate Trend
        daily_performance = delivered_orders.groupby(delivered_orders['order_date'].dt.date).apply(
            lambda x: (x['delivery_performance'] == 'On Time').sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
        daily_performance.columns = ['Date', 'On-Time Rate']
        
        fig_ontime_trend = px.line(
            daily_performance,
            x='Date',
            y='On-Time Rate',
            title='📈 Daily On-Time Delivery Rate (%)',
            template=theme['plotly_template']
        )
        fig_ontime_trend.update_traces(line_color=theme['success'], line_width=2)
        fig_ontime_trend.add_hline(y=80, line_dash="dash", line_color=theme['warning'],
                                    annotation_text="Target: 80%",
                                    annotation_font_color=theme['text_primary'])
        fig_ontime_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='On-Time Rate (%)', range=[0, 100]),
            hovermode='x unified'
        )
        st.plotly_chart(fig_ontime_trend, use_container_width=True)
    
    with chart_col2:
        # Stacked Bar Chart: Delay Breakdown (Prep Time vs Rider Time) by Zone
        delay_breakdown = delivered_orders.groupby('zone').agg({
            'prep_time_mins': 'mean',
            'rider_time_mins': 'mean'
        }).reset_index()
        delay_breakdown.columns = ['Zone', 'Avg Prep Time', 'Avg Rider Time']
        delay_breakdown = delay_breakdown.sort_values('Avg Prep Time', ascending=False).head(10)
        
        fig_delay_stack = go.Figure()
        fig_delay_stack.add_trace(go.Bar(
            name='Prep Time',
            x=delay_breakdown['Zone'],
            y=delay_breakdown['Avg Prep Time'],
            marker_color=theme['warning']
        ))
        fig_delay_stack.add_trace(go.Bar(
            name='Rider Time',
            x=delay_breakdown['Zone'],
            y=delay_breakdown['Avg Rider Time'],
            marker_color=theme['accent_secondary']
        ))
        fig_delay_stack.update_layout(
            barmode='stack',
            title='🕐 Delay Breakdown by Zone (Prep vs Rider Time)',
            template=theme['plotly_template'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Time (minutes)'),
            legend=dict(font=dict(color=theme['text_primary']))
        )
        st.plotly_chart(fig_delay_stack, use_container_width=True)
    
    # Row 2: Pareto Chart and Heatmap
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Pareto Chart: Cancellation Reasons
        cancel_reasons = cancelled_orders['cancellation_reason'].value_counts().reset_index()
        cancel_reasons.columns = ['Reason', 'Count']
        cancel_reasons['Cumulative %'] = (cancel_reasons['Count'].cumsum() / cancel_reasons['Count'].sum() * 100)
        
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_pareto.add_trace(
            go.Bar(name='Count', x=cancel_reasons['Reason'], y=cancel_reasons['Count'],
                   marker_color=theme['danger']),
            secondary_y=False
        )
        
        fig_pareto.add_trace(
            go.Scatter(name='Cumulative %', x=cancel_reasons['Reason'], y=cancel_reasons['Cumulative %'],
                       mode='lines+markers', marker_color=theme['accent'], line=dict(width=2)),
            secondary_y=True
        )
        
        fig_pareto.update_layout(
            title='📊 Cancellation Reasons (Pareto)',
            template=theme['plotly_template'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color']),
            legend=dict(font=dict(color=theme['text_primary']))
        )
        fig_pareto.update_yaxes(title_text="Count", secondary_y=False, gridcolor=theme['grid_color'])
        fig_pareto.update_yaxes(title_text="Cumulative %", secondary_y=True, gridcolor=theme['grid_color'])
        
        st.plotly_chart(fig_pareto, use_container_width=True)
    
    with chart_col4:
        # Heatmap: Performance by Hour of Day
        hourly_performance = delivered_orders.groupby('order_hour').apply(
            lambda x: (x['delivery_performance'] == 'On Time').sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
        hourly_performance.columns = ['Hour', 'On-Time Rate']
        
        # Create a simple bar chart styled as heatmap alternative
        fig_hourly = px.bar(
            hourly_performance,
            x='Hour',
            y='On-Time Rate',
            title='🕐 On-Time Rate by Hour of Day',
            template=theme['plotly_template'],
            color='On-Time Rate',
            color_continuous_scale=['#ff5252', '#ffab00', '#00c853']
        )
        fig_hourly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title='Hour', tickmode='linear', dtick=2),
            yaxis=dict(gridcolor=theme['grid_color'], title='On-Time Rate (%)', range=[0, 100]),
            coloraxis_showscale=False
        )
        # Highlight peak hours
        fig_hourly.add_vrect(x0=11.5, x1=14.5, fillcolor=theme['warning'], opacity=0.15, line_width=0,
                             annotation_text="Lunch", annotation_position="top")
        fig_hourly.add_vrect(x0=18.5, x1=22.5, fillcolor=theme['danger'], opacity=0.15, line_width=0,
                             annotation_text="Peak", annotation_position="top")
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    st.markdown("---")
    
    # --- TOP 10 PROBLEM AREAS TABLE (Sortable) ---
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🚨 Top 10 Problem Areas</h4>", unsafe_allow_html=True)
    
    problem_areas = delivered_orders.groupby('zone').agg({
        'order_id': 'count',
        'delivery_performance': lambda x: (x != 'On Time').sum(),
        'actual_delivery_time_mins': 'mean',
        'delay_reason': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A'
    }).reset_index()
    
    zone_cancellations = cancelled_orders.groupby('zone').size().reset_index()
    zone_cancellations.columns = ['zone', 'Cancellations']
    
    problem_areas = problem_areas.merge(zone_cancellations, on='zone', how='left')
    problem_areas['Cancellations'] = problem_areas['Cancellations'].fillna(0).astype(int)
    
    problem_areas.columns = ['Zone', 'Total Orders', 'Late Deliveries', 'Avg Delay (mins)', 'Top Delay Reason', 'Cancellations']
    problem_areas['Late %'] = (problem_areas['Late Deliveries'] / problem_areas['Total Orders'] * 100).round(1)
    problem_areas['Avg Delay (mins)'] = problem_areas['Avg Delay (mins)'].round(1)
    problem_areas = problem_areas.sort_values('Late Deliveries', ascending=False).head(10)
    
    problem_areas_display = problem_areas[['Zone', 'Late Deliveries', 'Late %', 'Avg Delay (mins)', 'Top Delay Reason', 'Cancellations']]
    
    st.dataframe(
        problem_areas_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Late Deliveries": st.column_config.NumberColumn(format="%d"),
            "Late %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
            "Avg Delay (mins)": st.column_config.NumberColumn(format="%.1f"),
            "Cancellations": st.column_config.NumberColumn(format="%d")
        }
    )
    
    st.markdown("---")
    
    # --- DRILL-DOWN BY ZONE ---
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🔍 Zone Drill-Down Analysis</h4>", unsafe_allow_html=True)
    
    drill_zone = st.selectbox(
        "Select a Zone to Drill Down",
        options=sorted(filtered_orders['zone'].dropna().unique().tolist()),
        index=0
    )
    
    zone_data = filtered_orders[filtered_orders['zone'] == drill_zone]
    zone_delivered = zone_data[zone_data['order_status'] == 'Delivered']
    zone_cancelled = zone_data[zone_data['order_status'] == 'Cancelled']
    
    drill_col1, drill_col2, drill_col3 = st.columns(3)
    
    with drill_col1:
        st.markdown(f"**📊 Zone Performance: {drill_zone}**")
        zone_on_time = (zone_delivered['delivery_performance'] == 'On Time').sum() / len(zone_delivered) * 100 if len(zone_delivered) > 0 else 0
        zone_avg_time = zone_delivered['actual_delivery_time_mins'].mean() if len(zone_delivered) > 0 else 0
        st.metric("On-Time Rate", f"{zone_on_time:.1f}%")
        st.metric("Avg Delivery Time", f"{zone_avg_time:.1f} mins")
    
    with drill_col2:
        st.markdown(f"**🏪 Restaurant Performance**")
        rest_perf = zone_delivered.groupby('restaurant_name')['prep_time_mins'].mean().reset_index()
        rest_perf.columns = ['Restaurant', 'Avg Prep Time']
        rest_perf = rest_perf.sort_values('Avg Prep Time', ascending=False).head(5)
        st.dataframe(rest_perf, use_container_width=True, hide_index=True)
    
    with drill_col3:
        st.markdown(f"**🏍️ Rider Performance**")
        rider_perf = zone_delivered.merge(riders[['rider_id', 'rider_name']], on='rider_id', how='left')
        rider_perf = rider_perf.groupby('rider_name')['rider_time_mins'].mean().reset_index()
        rider_perf.columns = ['Rider', 'Avg Delivery Time']
        rider_perf = rider_perf.sort_values('Avg Delivery Time', ascending=False).head(5)
        st.dataframe(rider_perf, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # =============================================================================
    # WHAT-IF ANALYSIS SECTION (MANDATORY FEATURE)
    # =============================================================================
    
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🎛️ What-If Analysis for Operations</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {theme['text_secondary']};'>Use the sliders below to simulate operational improvements</p>", unsafe_allow_html=True)
    
    whatif_col1, whatif_col2 = st.columns(2)
    
    with whatif_col1:
        prep_reduction = st.slider(
            "🍳 Reduce Avg Prep Time by (minutes)",
            min_value=1,
            max_value=15,
            value=5,
            step=1
        )
    
    with whatif_col2:
        cancel_reduction = st.slider(
            "❌ Reduce Cancellation Rate by (%)",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )
    
    # Calculate projections
    current_avg_total_time = avg_delivery_time
    projected_avg_time = max(current_avg_total_time - prep_reduction, 15)  # Min 15 mins
    
    # Assume on-time improves proportionally with reduced prep time
    time_improvement_ratio = prep_reduction / current_avg_total_time if current_avg_total_time > 0 else 0
    projected_on_time = min(on_time_rate + (time_improvement_ratio * 100 * 0.5), 100)  # Cap at 100%
    
    # Current late orders
    current_late_orders = total_delivered - len(on_time_orders)
    projected_late_orders = int(current_late_orders * (1 - time_improvement_ratio * 0.5))
    
    # Complaints (1 complaint per 5 late orders)
    current_complaints = current_late_orders / 5
    projected_complaints = projected_late_orders / 5
    complaint_reduction = current_complaints - projected_complaints
    
    # GMV recovery from reduced cancellations
    current_cancelled_gmv = cancelled_orders['gross_amount'].sum() if len(cancelled_orders) > 0 else 0
    avg_cancelled_order_value = cancelled_orders['gross_amount'].mean() if len(cancelled_orders) > 0 else 0
    orders_recovered = int(total_cancelled * (cancel_reduction / 100))
    gmv_recovery = orders_recovered * avg_cancelled_order_value
    
    new_cancellation_rate = cancellation_rate * (1 - cancel_reduction / 100)
    
    # Display projections
    st.markdown("<br>", unsafe_allow_html=True)
    
    proj_col1, proj_col2, proj_col3, proj_col4 = st.columns(4)
    
    with proj_col1:
        st.markdown(f"""
            <div class='what-if-card'>
                <h5 style='color: {theme["accent"]}; margin: 0;'>📈 Projected On-Time Rate</h5>
                <p style='font-size: 1.8rem; font-weight: bold; margin: 10px 0; color: {theme["success"]};'>{projected_on_time:.1f}%</p>
                <p style='color: {theme["text_secondary"]}; font-size: 0.9rem;'>Current: {on_time_rate:.1f}%</p>
            </div>
        """, unsafe_allow_html=True)
    
    with proj_col2:
        st.markdown(f"""
            <div class='what-if-card'>
                <h5 style='color: {theme["accent"]}; margin: 0;'>⏱️ Projected Delivery Time</h5>
                <p style='font-size: 1.8rem; font-weight: bold; margin: 10px 0; color: {theme["success"]};'>{projected_avg_time:.1f} mins</p>
                <p style='color: {theme["text_secondary"]}; font-size: 0.9rem;'>Current: {current_avg_total_time:.1f} mins</p>
            </div>
        """, unsafe_allow_html=True)
    
    with proj_col3:
        st.markdown(f"""
            <div class='what-if-card'>
                <h5 style='color: {theme["accent"]}; margin: 0;'>📞 Complaint Reduction</h5>
                <p style='font-size: 1.8rem; font-weight: bold; margin: 10px 0; color: {theme["success"]};'>-{complaint_reduction:.0f}</p>
                <p style='color: {theme["text_secondary"]}; font-size: 0.9rem;'>Fewer complaints expected</p>
            </div>
        """, unsafe_allow_html=True)
    
    with proj_col4:
        st.markdown(f"""
            <div class='what-if-card'>
                <h5 style='color: {theme["accent"]}; margin: 0;'>💰 GMV Recovery</h5>
                <p style='font-size: 1.8rem; font-weight: bold; margin: 10px 0; color: {theme["success"]};'>{format_currency(gmv_recovery)}</p>
                <p style='color: {theme["text_secondary"]}; font-size: 0.9rem;'>From {orders_recovered} recovered orders</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # =============================================================================
    # RIDER PERFORMANCE TIERS (OPTIONAL FEATURE - IMPLEMENTED)
    # =============================================================================
    
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🏍️ Rider Performance Tiers</h4>", unsafe_allow_html=True)
    
    # Calculate rider stats
    rider_stats = delivered_orders.groupby('rider_id').agg({
        'order_id': 'count',
        'actual_delivery_time_mins': 'mean',
        'delivery_performance': lambda x: (x == 'On Time').sum() / len(x) * 100 if len(x) > 0 else 0
    }).reset_index()
    rider_stats.columns = ['rider_id', 'deliveries', 'avg_time', 'on_time_rate']
    
    # Classify riders
    rider_stats['tier'] = rider_stats.apply(
        lambda x: classify_rider_tier(x['avg_time'], x['on_time_rate']), axis=1
    )
    
    # Merge with rider names
    rider_stats = rider_stats.merge(riders[['rider_id', 'rider_name', 'city', 'vehicle_type']], on='rider_id', how='left')
    
    # Tier distribution
    tier_dist = rider_stats['tier'].value_counts().reset_index()
    tier_dist.columns = ['Tier', 'Count']
    
    tier_col1, tier_col2 = st.columns([1, 2])
    
    with tier_col1:
        tier_colors = {
            'Star Rider': theme['success'],
            'Good Rider': theme['accent_secondary'],
            'Needs Improvement': theme['warning'],
            'At Risk': theme['danger']
        }
        
        fig_tier = px.pie(
            tier_dist,
            values='Count',
            names='Tier',
            title='Rider Tier Distribution',
            template=theme['plotly_template'],
            color='Tier',
            color_discrete_map=tier_colors
        )
        fig_tier.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            legend=dict(font=dict(color=theme['text_primary']))
        )
        st.plotly_chart(fig_tier, use_container_width=True)
    
    with tier_col2:
        # Filter by tier
        selected_tier = st.selectbox(
            "Filter by Tier",
            options=['All'] + list(tier_dist['Tier']),
            index=0
        )
        
        if selected_tier != 'All':
            display_riders = rider_stats[rider_stats['tier'] == selected_tier]
        else:
            display_riders = rider_stats
        
        display_riders_table = display_riders[['rider_name', 'city', 'vehicle_type', 'deliveries', 'avg_time', 'on_time_rate', 'tier']]
        display_riders_table.columns = ['Rider Name', 'City', 'Vehicle', 'Deliveries', 'Avg Time (mins)', 'On-Time %', 'Tier']
        display_riders_table['Avg Time (mins)'] = display_riders_table['Avg Time (mins)'].round(1)
        display_riders_table['On-Time %'] = display_riders_table['On-Time %'].round(1)
        display_riders_table = display_riders_table.sort_values('On-Time %', ascending=False).head(15)
        
        st.dataframe(
            display_riders_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Deliveries": st.column_config.NumberColumn(format="%d"),
                "Avg Time (mins)": st.column_config.NumberColumn(format="%.1f"),
                "On-Time %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%")
            }
        )

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; padding: 20px; color: {theme["text_secondary"]};'>
        <p>🍔 <strong>BitesUAE Dashboard</strong> | Built with Streamlit & Plotly</p>
        <p style='font-size: 0.8rem;'>Data is synthetically generated for demonstration purposes | UAE Food Delivery Analytics</p>
    </div>
""", unsafe_allow_html=True)
