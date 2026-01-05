# =============================================================================
# BitesUAE - Food Delivery CX & Operations Dashboard
# Main Streamlit Application
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

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme color schemes
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
        'chart_bg': 'rgba(30, 33, 48, 0.8)',
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
        'chart_bg': 'rgba(248, 249, 250, 0.8)',
        'grid_color': '#e0e0e0',
        'plotly_template': 'plotly_white'
    }
}

# Get current theme colors
theme = THEMES[st.session_state.theme]

# =============================================================================
# CUSTOM CSS BASED ON THEME
# =============================================================================

def get_css(theme):
    return f"""
    <style>
        /* Main app background */
        .stApp {{
            background-color: {theme['bg_color']};
        }}
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: {theme['card_bg']};
            border-right: 1px solid {theme['card_border']};
        }}
        
        section[data-testid="stSidebar"] .stMarkdown {{
            color: {theme['text_primary']};
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Regular text */
        p, span, label {{
            color: {theme['text_primary']};
        }}
        
        /* Metric container styling */
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
        
        div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {{
            font-weight: 500;
        }}
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {theme['card_bg']};
            border-radius: 10px;
            padding: 12px 24px;
            color: {theme['text_secondary']};
            border: 1px solid {theme['card_border']};
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {theme['accent']};
            color: white !important;
            border: none;
        }}
        
        /* Selectbox styling */
        .stSelectbox label {{
            color: {theme['text_primary']} !important;
        }}
        
        .stSelectbox > div > div {{
            background-color: {theme['card_bg']};
            border-color: {theme['card_border']};
            color: {theme['text_primary']};
        }}
        
        /* Date input styling */
        .stDateInput label {{
            color: {theme['text_primary']} !important;
        }}
        
        .stDateInput > div > div {{
            background-color: {theme['card_bg']};
            border-color: {theme['card_border']};
        }}
        
        /* Multiselect styling */
        .stMultiSelect label {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: {theme['card_bg']};
            color: {theme['text_primary']} !important;
            border-radius: 10px;
        }}
        
        /* Divider */
        hr {{
            border-color: {theme['card_border']};
        }}
        
        /* DataFrame styling */
        .stDataFrame {{
            background-color: {theme['card_bg']};
            border-radius: 10px;
        }}
        
        /* Custom card class */
        .custom-card {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
        }}
        
        /* KPI highlight colors */
        .kpi-positive {{
            color: {theme['success']};
        }}
        
        .kpi-negative {{
            color: {theme['danger']};
        }}
        
        .kpi-neutral {{
            color: {theme['warning']};
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {theme['accent']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        .stButton > button:hover {{
            background-color: {theme['accent_secondary']};
        }}
        
        /* Toggle button specific */
        .theme-toggle {{
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 999;
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
        xlsx = pd.ExcelFile('data/cleaned/BitesUAE_Cleaned.xlsx')
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

def calculate_delta(current, previous):
    """Calculate percentage change."""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def get_chart_colors(theme_name):
    """Get color palette for charts based on theme."""
    if theme_name == 'dark':
        return ['#ff6b35', '#4da6ff', '#00c853', '#ffab00', '#ff5252', '#9c27b0', '#00bcd4', '#8bc34a']
    else:
        return ['#ff6b35', '#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#65a30d']

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Logo and Title
    st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: {theme["accent"]}; font-size: 2.5rem; margin: 0;'>🍔</h1>
            <h2 style='color: {theme["text_primary"]}; margin: 5px 0;'>BitesUAE</h2>
            <p style='color: {theme["text_secondary"]}; font-size: 0.9rem;'>Delivery Analytics</p>
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
    
    # Date Filter
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
    
    # City Filter
    st.subheader("🏙️ City")
    orders_with_city = orders.merge(
        restaurants[['restaurant_id', 'city']], 
        on='restaurant_id', 
        how='left'
    )
    cities = ['All Cities'] + sorted(orders_with_city['city'].dropna().unique().tolist())
    selected_city = st.selectbox("Select City", cities, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Cuisine Filter
    st.subheader("🍽️ Cuisine Type")
    cuisines = ['All Cuisines'] + sorted(restaurants['cuisine_type'].dropna().unique().tolist())
    selected_cuisine = st.selectbox("Select Cuisine", cuisines, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Order Status Filter
    st.subheader("📦 Order Status")
    statuses = ['All Statuses'] + sorted(orders['order_status'].dropna().unique().tolist())
    selected_status = st.selectbox("Select Status", statuses, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Footer
    st.markdown(f"""
        <div style='text-align: center; padding: 20px 0;'>
            <p style='color: {theme["text_secondary"]}; font-size: 0.8rem;'>
                Built with ❤️ for Portfolio<br>
                UAE Food Delivery Analytics
            </p>
        </div>
    """, unsafe_allow_html=True)

# =============================================================================
# APPLY FILTERS
# =============================================================================

# Merge orders with restaurant info
orders_enriched = orders.merge(
    restaurants[['restaurant_id', 'city', 'cuisine_type', 'restaurant_tier', 'restaurant_name', 'rating']], 
    on='restaurant_id',
    how='left'
)

# Merge with delivery events
orders_full = orders_enriched.merge(
    delivery_events[['order_id', 'rider_id', 'actual_delivery_time_mins', 'delivered_time', 
                     'estimated_delivery_time', 'delay_reason', 'delivery_performance']],
    on='order_id',
    how='left'
)

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
if selected_city != 'All Cities':
    filtered_orders = filtered_orders[filtered_orders['city'] == selected_city]

# Cuisine filter
if selected_cuisine != 'All Cuisines':
    filtered_orders = filtered_orders[filtered_orders['cuisine_type'] == selected_cuisine]

# Status filter
if selected_status != 'All Statuses':
    filtered_orders = filtered_orders[filtered_orders['order_status'] == selected_status]

# =============================================================================
# CALCULATE KPIs
# =============================================================================

# Total metrics
total_orders = len(filtered_orders)
total_revenue = filtered_orders['net_amount'].sum()
avg_order_value = filtered_orders['net_amount'].mean() if total_orders > 0 else 0

# Delivered orders only for delivery metrics
delivered_orders = filtered_orders[filtered_orders['order_status'] == 'Delivered']
total_delivered = len(delivered_orders)

# Delivery performance
on_time_orders = delivered_orders[delivered_orders['delivery_performance'] == 'On Time']
on_time_rate = (len(on_time_orders) / total_delivered * 100) if total_delivered > 0 else 0
avg_delivery_time = delivered_orders['actual_delivery_time_mins'].mean() if total_delivered > 0 else 0

# Cancellation rate
cancelled_orders = filtered_orders[filtered_orders['order_status'] == 'Cancelled']
cancellation_rate = (len(cancelled_orders) / total_orders * 100) if total_orders > 0 else 0

# Customer metrics
unique_customers = filtered_orders['customer_id'].nunique()

# Calculate previous period for comparison (mock delta values for demo)
delta_revenue = 12.5
delta_orders = 8.3
delta_aov = 3.2
delta_delivery = -2.1

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

# Header
st.markdown(f"""
    <div style='padding: 20px 0;'>
        <h1 style='color: {theme["text_primary"]}; font-size: 2.5rem; font-weight: 700; margin: 0;'>
            📊 Operations Dashboard
        </h1>
        <p style='color: {theme["text_secondary"]}; font-size: 1.1rem; margin-top: 5px;'>
            Real-time insights into BitesUAE food delivery operations
        </p>
    </div>
""", unsafe_allow_html=True)

# Display active filters
filter_text = []
if selected_city != 'All Cities':
    filter_text.append(f"🏙️ {selected_city}")
if selected_cuisine != 'All Cuisines':
    filter_text.append(f"🍽️ {selected_cuisine}")
if selected_status != 'All Statuses':
    filter_text.append(f"📦 {selected_status}")

if filter_text:
    st.markdown(f"""
        <div style='background-color: {theme["card_bg"]}; padding: 10px 20px; border-radius: 8px; 
                    border-left: 4px solid {theme["accent"]}; margin-bottom: 20px;'>
            <span style='color: {theme["text_secondary"]};'>Active Filters: </span>
            <span style='color: {theme["text_primary"]};'>{' | '.join(filter_text)}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# KPI CARDS ROW
# =============================================================================

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.metric(
        label="💰 Total Revenue",
        value=format_currency(total_revenue),
        delta=f"{delta_revenue:+.1f}%"
    )

with kpi_col2:
    st.metric(
        label="📦 Total Orders",
        value=format_number(total_orders),
        delta=f"{delta_orders:+.1f}%"
    )

with kpi_col3:
    st.metric(
        label="🧾 Avg Order Value",
        value=f"AED {avg_order_value:.2f}",
        delta=f"{delta_aov:+.1f}%"
    )

with kpi_col4:
    st.metric(
        label="⏱️ On-Time Delivery",
        value=f"{on_time_rate:.1f}%",
        delta=f"{delta_delivery:+.1f}%",
        delta_color="inverse"
    )

with kpi_col5:
    st.metric(
        label="❌ Cancellation Rate",
        value=f"{cancellation_rate:.1f}%",
        delta=f"-1.2%",
        delta_color="inverse"
    )

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# TABS FOR DIFFERENT VIEWS
# =============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview", 
    "🚚 Delivery Performance", 
    "👥 Customer Analytics",
    "🏪 Restaurant Insights",
    "📋 Data Explorer"
])

# Chart colors based on theme
chart_colors = get_chart_colors(st.session_state.theme)

# =============================================================================
# TAB 1: OVERVIEW
# =============================================================================

with tab1:
    st.markdown(f"<h3 style='color: {theme['text_primary']};'>Revenue & Order Trends</h3>", unsafe_allow_html=True)
    
    # Row 1: Revenue and Orders Trend
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Revenue Trend
        daily_revenue = filtered_orders.groupby(filtered_orders['order_date'].dt.date)['net_amount'].sum().reset_index()
        daily_revenue.columns = ['Date', 'Revenue']
        
        fig_revenue = px.area(
            daily_revenue,
            x='Date',
            y='Revenue',
            title='Daily Revenue Trend',
            template=theme['plotly_template']
        )
        fig_revenue.update_traces(
            fill='tozeroy',
            line_color=theme['accent'],
            fillcolor=f"rgba(255, 107, 53, 0.3)"
        )
        fig_revenue.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Revenue (AED)'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Daily Orders Trend
        daily_orders = filtered_orders.groupby(filtered_orders['order_date'].dt.date).size().reset_index()
        daily_orders.columns = ['Date', 'Orders']
        
        fig_orders = px.line(
            daily_orders,
            x='Date',
            y='Orders',
            title='Daily Orders Trend',
            template=theme['plotly_template']
        )
        fig_orders.update_traces(
            line_color=theme['accent_secondary'],
            line_width=2
        )
        fig_orders.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Number of Orders'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: City and Cuisine breakdown
    col3, col4 = st.columns(2)
    
    with col3:
        # Revenue by City
        city_revenue = filtered_orders.groupby('city')['net_amount'].sum().reset_index()
        city_revenue.columns = ['City', 'Revenue']
        city_revenue = city_revenue.sort_values('Revenue', ascending=True)
        
        fig_city = px.bar(
            city_revenue,
            x='Revenue',
            y='City',
            orientation='h',
            title='Revenue by City',
            template=theme['plotly_template'],
            color='Revenue',
            color_continuous_scale=['#ff6b35', '#ffab00']
        )
        fig_city.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title='Revenue (AED)'),
            yaxis=dict(gridcolor=theme['grid_color'], title=''),
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_city, use_container_width=True)
    
    with col4:
        # Orders by Cuisine Type
        cuisine_orders = filtered_orders.groupby('cuisine_type').size().reset_index()
        cuisine_orders.columns = ['Cuisine', 'Orders']
        
        fig_cuisine = px.pie(
            cuisine_orders,
            values='Orders',
            names='Cuisine',
            title='Orders by Cuisine Type',
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
    
    st.markdown("---")
    
    # Row 3: Hourly Pattern and Payment Methods
    col5, col6 = st.columns(2)
    
    with col5:
        # Orders by Hour
        if 'order_hour' in filtered_orders.columns:
            hourly_orders = filtered_orders.groupby('order_hour').size().reset_index()
        else:
            filtered_orders['order_hour'] = filtered_orders['order_datetime'].dt.hour
            hourly_orders = filtered_orders.groupby('order_hour').size().reset_index()
        hourly_orders.columns = ['Hour', 'Orders']
        
        fig_hourly = px.bar(
            hourly_orders,
            x='Hour',
            y='Orders',
            title='Orders by Hour of Day',
            template=theme['plotly_template']
        )
        fig_hourly.update_traces(marker_color=theme['accent'])
        fig_hourly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(
                gridcolor=theme['grid_color'], 
                title='Hour of Day',
                tickmode='linear',
                dtick=2
            ),
            yaxis=dict(gridcolor=theme['grid_color'], title='Number of Orders'),
            bargap=0.2
        )
        # Highlight peak hours
        fig_hourly.add_vrect(x0=11.5, x1=13.5, fillcolor=theme['warning'], opacity=0.2, line_width=0)
        fig_hourly.add_vrect(x0=18.5, x1=21.5, fillcolor=theme['warning'], opacity=0.2, line_width=0)
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col6:
        # Payment Methods
        payment_dist = filtered_orders.groupby('payment_method').size().reset_index()
        payment_dist.columns = ['Payment Method', 'Orders']
        
        fig_payment = px.pie(
            payment_dist,
            values='Orders',
            names='Payment Method',
            title='Payment Methods Distribution',
            template=theme['plotly_template'],
            color_discrete_sequence=chart_colors
        )
        fig_payment.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            legend=dict(font=dict(color=theme['text_primary']))
        )
        fig_payment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment, use_container_width=True)

# =============================================================================
# TAB 2: DELIVERY PERFORMANCE
# =============================================================================

with tab2:
    st.markdown(f"<h3 style='color: {theme['text_primary']};'>Delivery Operations Analysis</h3>", unsafe_allow_html=True)
    
    # Delivery KPIs
    del_col1, del_col2, del_col3, del_col4 = st.columns(4)
    
    with del_col1:
        st.metric(
            label="✅ Delivered Orders",
            value=format_number(total_delivered),
            delta=f"{(total_delivered/total_orders*100):.1f}% of total" if total_orders > 0 else "N/A"
        )
    
    with del_col2:
        st.metric(
            label="⏱️ Avg Delivery Time",
            value=f"{avg_delivery_time:.1f} mins",
            delta="-2.3 mins vs last period"
        )
    
    with del_col3:
        late_orders = len(delivered_orders[delivered_orders['delivery_performance'].isin(['Late (<15 min)', 'Late (>15 min)'])])
        late_rate = (late_orders / total_delivered * 100) if total_delivered > 0 else 0
        st.metric(
            label="⚠️ Late Deliveries",
            value=f"{late_rate:.1f}%",
            delta="-3.1%",
            delta_color="inverse"
        )
    
    with del_col4:
        active_riders = len(riders[riders['rider_status'] == 'Active'])
        st.metric(
            label="🏍️ Active Riders",
            value=format_number(active_riders),
            delta="+12 this month"
        )
    
    st.markdown("---")
    
    # Delivery Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Delivery Performance Distribution
        if 'delivery_performance' in delivered_orders.columns:
            perf_dist = delivered_orders['delivery_performance'].value_counts().reset_index()
            perf_dist.columns = ['Performance', 'Count']
            
            # Custom colors for performance
            perf_colors = {
                'On Time': theme['success'],
                'Late (<15 min)': theme['warning'],
                'Late (>15 min)': theme['danger'],
                'Not Delivered': theme['text_secondary']
            }
            colors = [perf_colors.get(p, theme['accent']) for p in perf_dist['Performance']]
            
            fig_perf = px.pie(
                perf_dist,
                values='Count',
                names='Performance',
                title='Delivery Performance Distribution',
                template=theme['plotly_template'],
                color='Performance',
                color_discrete_map=perf_colors
            )
            fig_perf.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color=theme['text_primary'],
                title_font_color=theme['text_primary'],
                legend=dict(font=dict(color=theme['text_primary']))
            )
            fig_perf.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_perf, use_container_width=True)
    
    with col2:
        # Delay Reasons
        delayed_orders = delivered_orders[delivered_orders['delay_reason'].notna()]
        if len(delayed_orders) > 0:
            delay_reasons = delayed_orders['delay_reason'].value_counts().reset_index()
            delay_reasons.columns = ['Reason', 'Count']
            
            fig_delay = px.bar(
                delay_reasons,
                x='Count',
                y='Reason',
                orientation='h',
                title='Top Delay Reasons',
                template=theme['plotly_template']
            )
            fig_delay.update_traces(marker_color=theme['danger'])
            fig_delay.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color=theme['text_primary'],
                title_font_color=theme['text_primary'],
                xaxis=dict(gridcolor=theme['grid_color'], title='Number of Orders'),
                yaxis=dict(gridcolor=theme['grid_color'], title=''),
            )
            st.plotly_chart(fig_delay, use_container_width=True)
        else:
            st.info("No delay data available for the selected filters.")
    
    st.markdown("---")
    
    # Row 2: Delivery Time Distribution and City Performance
    col3, col4 = st.columns(2)
    
    with col3:
        # Delivery Time Distribution
        valid_times = delivered_orders[delivered_orders['actual_delivery_time_mins'].notna()]['actual_delivery_time_mins']
        if len(valid_times) > 0:
            fig_time_dist = px.histogram(
                valid_times,
                nbins=30,
                title='Delivery Time Distribution',
                template=theme['plotly_template'],
                labels={'value': 'Delivery Time (mins)', 'count': 'Frequency'}
            )
            fig_time_dist.update_traces(marker_color=theme['accent_secondary'])
            fig_time_dist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color=theme['text_primary'],
                title_font_color=theme['text_primary'],
                xaxis=dict(gridcolor=theme['grid_color'], title='Delivery Time (minutes)'),
                yaxis=dict(gridcolor=theme['grid_color'], title='Number of Deliveries'),
                showlegend=False
            )
            # Add average line
            avg_time = valid_times.mean()
            fig_time_dist.add_vline(x=avg_time, line_dash="dash", line_color=theme['warning'],
                                     annotation_text=f"Avg: {avg_time:.1f} mins",
                                     annotation_font_color=theme['text_primary'])
            st.plotly_chart(fig_time_dist, use_container_width=True)
    
    with col4:
        # On-Time Rate by City
        city_performance = delivered_orders.groupby('city').apply(
            lambda x: (x['delivery_performance'] == 'On Time').sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
        city_performance.columns = ['City', 'On-Time Rate']
        city_performance = city_performance.sort_values('On-Time Rate', ascending=True)
        
        fig_city_perf = px.bar(
            city_performance,
            x='On-Time Rate',
            y='City',
            orientation='h',
            title='On-Time Delivery Rate by City',
            template=theme['plotly_template']
        )
        fig_city_perf.update_traces(marker_color=theme['success'])
        fig_city_perf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title='On-Time Rate (%)', range=[0, 100]),
            yaxis=dict(gridcolor=theme['grid_color'], title=''),
        )
        # Add target line
        fig_city_perf.add_vline(x=80, line_dash="dash", line_color=theme['warning'],
                                 annotation_text="Target: 80%",
                                 annotation_font_color=theme['text_primary'])
        st.plotly_chart(fig_city_perf, use_container_width=True)
    
    st.markdown("---")
    
    # Rider Performance Table
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🏍️ Top Performing Riders</h4>", unsafe_allow_html=True)
    
    rider_stats = delivered_orders.groupby('rider_id').agg({
        'order_id': 'count',
        'actual_delivery_time_mins': 'mean',
        'delivery_performance': lambda x: (x == 'On Time').sum() / len(x) * 100 if len(x) > 0 else 0
    }).reset_index()
    rider_stats.columns = ['Rider ID', 'Total Deliveries', 'Avg Delivery Time (mins)', 'On-Time Rate (%)']
    rider_stats = rider_stats.merge(riders[['rider_id', 'rider_name', 'city', 'vehicle_type']], 
                                     left_on='Rider ID', right_on='rider_id', how='left')
    rider_stats = rider_stats[['rider_name', 'city', 'vehicle_type', 'Total Deliveries', 
                                'Avg Delivery Time (mins)', 'On-Time Rate (%)']]
    rider_stats.columns = ['Rider Name', 'City', 'Vehicle', 'Deliveries', 'Avg Time (mins)', 'On-Time %']
    rider_stats['Avg Time (mins)'] = rider_stats['Avg Time (mins)'].round(1)
    rider_stats['On-Time %'] = rider_stats['On-Time %'].round(1)
    rider_stats = rider_stats.sort_values('On-Time %', ascending=False).head(10)
    
    st.dataframe(
        rider_stats,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Deliveries": st.column_config.NumberColumn(format="%d"),
            "Avg Time (mins)": st.column_config.NumberColumn(format="%.1f"),
            "On-Time %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%")
        }
    )

# =============================================================================
# TAB 3: CUSTOMER ANALYTICS
# =============================================================================

with tab3:
    st.markdown(f"<h3 style='color: {theme['text_primary']};'>Customer Insights</h3>", unsafe_allow_html=True)
    
    # Customer KPIs
    cust_col1, cust_col2, cust_col3, cust_col4 = st.columns(4)
    
    # Calculate customer metrics
    customer_orders = filtered_orders.groupby('customer_id').agg({
        'order_id': 'count',
        'net_amount': 'sum'
    }).reset_index()
    customer_orders.columns = ['customer_id', 'order_count', 'total_spent']
    
    avg_orders_per_customer = customer_orders['order_count'].mean() if len(customer_orders) > 0 else 0
    avg_ltv = customer_orders['total_spent'].mean() if len(customer_orders) > 0 else 0
    repeat_customers = len(customer_orders[customer_orders['order_count'] > 1])
    repeat_rate = (repeat_customers / len(customer_orders) * 100) if len(customer_orders) > 0 else 0
    
    with cust_col1:
        st.metric(
            label="👥 Unique Customers",
            value=format_number(unique_customers),
            delta="+523 this month"
        )
    
    with cust_col2:
        st.metric(
            label="📊 Avg Orders/Customer",
            value=f"{avg_orders_per_customer:.2f}",
            delta="+0.3 vs last period"
        )
    
    with cust_col3:
        st.metric(
            label="💰 Avg Customer LTV",
            value=format_currency(avg_ltv),
            delta="+8.2%"
        )
    
    with cust_col4:
        st.metric(
            label="🔄 Repeat Customer Rate",
            value=f"{repeat_rate:.1f}%",
            delta="+2.1%"
        )
    
    st.markdown("---")
    
    # Customer Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Tier Distribution
        customer_tiers = customers.merge(
            filtered_orders[['customer_id']].drop_duplicates(), 
            on='customer_id', 
            how='inner'
        )
        tier_dist = customer_tiers['customer_tier'].value_counts().reset_index()
        tier_dist.columns = ['Tier', 'Count']
        
        # Order tiers logically
        tier_order = ['New', 'Regular', 'Loyal', 'VIP']
        tier_dist['Tier'] = pd.Categorical(tier_dist['Tier'], categories=tier_order, ordered=True)
        tier_dist = tier_dist.sort_values('Tier')
        
        fig_tier = px.bar(
            tier_dist,
            x='Tier',
            y='Count',
            title='Customer Tier Distribution',
            template=theme['plotly_template'],
            color='Tier',
            color_discrete_sequence=chart_colors
        )
        fig_tier.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Number of Customers'),
            showlegend=False
        )
        st.plotly_chart(fig_tier, use_container_width=True)
    
    with col2:
        # Customer Acquisition by Signup Source
        customer_sources = customers.merge(
            filtered_orders[['customer_id']].drop_duplicates(), 
            on='customer_id', 
            how='inner'
        )
        source_dist = customer_sources['signup_source'].value_counts().reset_index()
        source_dist.columns = ['Source', 'Count']
        
        fig_source = px.pie(
            source_dist,
            values='Count',
            names='Source',
            title='Customer Acquisition Sources',
            template=theme['plotly_template'],
            color_discrete_sequence=chart_colors,
            hole=0.4
        )
        fig_source.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            legend=dict(font=dict(color=theme['text_primary']))
        )
        fig_source.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_source, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: Customer Spending Distribution and City Distribution
    col3, col4 = st.columns(2)
    
    with col3:
        # Customer Order Frequency Distribution
        order_freq = customer_orders['order_count'].value_counts().reset_index()
        order_freq.columns = ['Orders', 'Customers']
        order_freq = order_freq.sort_values('Orders')
        
        # Bucket high values
        order_freq_bucketed = order_freq.copy()
        order_freq_bucketed.loc[order_freq_bucketed['Orders'] > 10, 'Orders'] = '10+'
        order_freq_bucketed = order_freq_bucketed.groupby('Orders')['Customers'].sum().reset_index()
        
        fig_freq = px.bar(
            order_freq_bucketed,
            x='Orders',
            y='Customers',
            title='Order Frequency Distribution',
            template=theme['plotly_template']
        )
        fig_freq.update_traces(marker_color=theme['accent'])
        fig_freq.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title='Number of Orders'),
            yaxis=dict(gridcolor=theme['grid_color'], title='Number of Customers'),
        )
        st.plotly_chart(fig_freq, use_container_width=True)
    
    with col4:
        # Revenue by Customer Tier
        tier_revenue = filtered_orders.merge(customers[['customer_id', 'customer_tier']], on='customer_id', how='left')
        tier_revenue_agg = tier_revenue.groupby('customer_tier')['net_amount'].sum().reset_index()
        tier_revenue_agg.columns = ['Tier', 'Revenue']
        
        # Order tiers logically
        tier_revenue_agg['Tier'] = pd.Categorical(tier_revenue_agg['Tier'], categories=tier_order, ordered=True)
        tier_revenue_agg = tier_revenue_agg.sort_values('Tier')
        
        fig_tier_rev = px.bar(
            tier_revenue_agg,
            x='Tier',
            y='Revenue',
            title='Revenue by Customer Tier',
            template=theme['plotly_template'],
            color='Tier',
            color_discrete_sequence=chart_colors
        )
        fig_tier_rev.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Revenue (AED)'),
            showlegend=False
        )
        st.plotly_chart(fig_tier_rev, use_container_width=True)
    
    st.markdown("---")
    
    # Top Customers Table
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🏆 Top Customers by Revenue</h4>", unsafe_allow_html=True)
    
    top_customers = customer_orders.merge(
        customers[['customer_id', 'customer_name', 'city', 'customer_tier']], 
        on='customer_id', 
        how='left'
    )
    top_customers = top_customers.sort_values('total_spent', ascending=False).head(10)
    top_customers = top_customers[['customer_name', 'city', 'customer_tier', 'order_count', 'total_spent']]
    top_customers.columns = ['Customer Name', 'City', 'Tier', 'Orders', 'Total Spent (AED)']
    top_customers['Total Spent (AED)'] = top_customers['Total Spent (AED)'].round(2)
    
    st.dataframe(
        top_customers,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Orders": st.column_config.NumberColumn(format="%d"),
            "Total Spent (AED)": st.column_config.NumberColumn(format="AED %.2f")
        }
    )

# =============================================================================
# TAB 4: RESTAURANT INSIGHTS
# =============================================================================

with tab4:
    st.markdown(f"<h3 style='color: {theme['text_primary']};'>Restaurant Performance</h3>", unsafe_allow_html=True)
    
    # Restaurant KPIs
    rest_col1, rest_col2, rest_col3, rest_col4 = st.columns(4)
    
    # Calculate restaurant metrics
    restaurant_stats = filtered_orders.groupby('restaurant_id').agg({
        'order_id': 'count',
        'net_amount': 'sum',
        'rating': 'first'
    }).reset_index()
    restaurant_stats.columns = ['restaurant_id', 'order_count', 'total_revenue', 'rating']
    
    active_restaurants = restaurant_stats['restaurant_id'].nunique()
    avg_rating = restaurants['rating'].mean()
    top_cuisine = filtered_orders['cuisine_type'].value_counts().index[0] if len(filtered_orders) > 0 else "N/A"
    avg_prep_time = restaurants['avg_prep_time_mins'].mean()
    
    with rest_col1:
        st.metric(
            label="🏪 Active Restaurants",
            value=format_number(active_restaurants),
            delta="+15 this month"
        )
    
    with rest_col2:
        st.metric(
            label="⭐ Avg Restaurant Rating",
            value=f"{avg_rating:.2f}",
            delta="+0.1"
        )
    
    with rest_col3:
        st.metric(
            label="🍽️ Top Cuisine",
            value=top_cuisine,
            delta="32% of orders"
        )
    
    with rest_col4:
        st.metric(
            label="⏰ Avg Prep Time",
            value=f"{avg_prep_time:.1f} mins",
            delta="-1.5 mins"
        )
    
    st.markdown("---")
    
    # Restaurant Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Restaurant Tier Distribution
        tier_dist_rest = filtered_orders.groupby('restaurant_tier').agg({
            'order_id': 'count',
            'net_amount': 'sum'
        }).reset_index()
        tier_dist_rest.columns = ['Tier', 'Orders', 'Revenue']
        
        fig_rest_tier = px.bar(
            tier_dist_rest,
            x='Tier',
            y='Revenue',
            title='Revenue by Restaurant Tier',
            template=theme['plotly_template'],
            color='Tier',
            color_discrete_sequence=chart_colors
        )
        fig_rest_tier.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Revenue (AED)'),
            showlegend=False
        )
        st.plotly_chart(fig_rest_tier, use_container_width=True)
    
    with col2:
        # Rating Distribution
        rating_bins = pd.cut(restaurants['rating'], bins=[0, 3, 3.5, 4, 4.5, 5], 
                            labels=['1-3', '3-3.5', '3.5-4', '4-4.5', '4.5-5'])
        rating_dist = rating_bins.value_counts().reset_index()
        rating_dist.columns = ['Rating Range', 'Count']
        rating_dist = rating_dist.sort_values('Rating Range')
        
        fig_rating = px.bar(
            rating_dist,
            x='Rating Range',
            y='Count',
            title='Restaurant Rating Distribution',
            template=theme['plotly_template']
        )
        fig_rating.update_traces(marker_color=theme['warning'])
        fig_rating.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title='Rating Range'),
            yaxis=dict(gridcolor=theme['grid_color'], title='Number of Restaurants'),
        )
        st.plotly_chart(fig_rating, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2
    col3, col4 = st.columns(2)
    
    with col3:
        # Cuisine Performance
        cuisine_perf = filtered_orders.groupby('cuisine_type').agg({
            'order_id': 'count',
            'net_amount': ['sum', 'mean']
        }).reset_index()
        cuisine_perf.columns = ['Cuisine', 'Orders', 'Total Revenue', 'Avg Order Value']
        cuisine_perf = cuisine_perf.sort_values('Total Revenue', ascending=False)
        
        fig_cuisine_perf = px.bar(
            cuisine_perf,
            x='Cuisine',
            y='Total Revenue',
            title='Revenue by Cuisine Type',
            template=theme['plotly_template'],
            color='Cuisine',
            color_discrete_sequence=chart_colors
        )
        fig_cuisine_perf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Revenue (AED)'),
            showlegend=False
        )
        st.plotly_chart(fig_cuisine_perf, use_container_width=True)
    
    with col4:
        # Prep Time by Tier
        prep_by_tier = restaurants.groupby('restaurant_tier')['avg_prep_time_mins'].mean().reset_index()
        prep_by_tier.columns = ['Tier', 'Avg Prep Time']
        
        fig_prep = px.bar(
            prep_by_tier,
            x='Tier',
            y='Avg Prep Time',
            title='Average Prep Time by Restaurant Tier',
            template=theme['plotly_template']
        )
        fig_prep.update_traces(marker_color=theme['accent_secondary'])
        fig_prep.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme['text_primary'],
            title_font_color=theme['text_primary'],
            xaxis=dict(gridcolor=theme['grid_color'], title=''),
            yaxis=dict(gridcolor=theme['grid_color'], title='Prep Time (minutes)'),
        )
        st.plotly_chart(fig_prep, use_container_width=True)
    
    st.markdown("---")
    
    # Top Restaurants Table
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>🏆 Top Performing Restaurants</h4>", unsafe_allow_html=True)
    
    top_restaurants = restaurant_stats.merge(
        restaurants[['restaurant_id', 'restaurant_name', 'city', 'cuisine_type', 'restaurant_tier', 'rating']], 
        on='restaurant_id', 
        how='left'
    )
    top_restaurants = top_restaurants.sort_values('total_revenue', ascending=False).head(10)
    top_restaurants = top_restaurants[['restaurant_name', 'city', 'cuisine_type', 'restaurant_tier', 
                                        'order_count', 'total_revenue', 'rating_y']]
    top_restaurants.columns = ['Restaurant', 'City', 'Cuisine', 'Tier', 'Orders', 'Revenue (AED)', 'Rating']
    top_restaurants['Revenue (AED)'] = top_restaurants['Revenue (AED)'].round(2)
    
    st.dataframe(
        top_restaurants,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Orders": st.column_config.NumberColumn(format="%d"),
            "Revenue (AED)": st.column_config.NumberColumn(format="AED %.2f"),
            "Rating": st.column_config.NumberColumn(format="⭐ %.1f")
        }
    )

# =============================================================================
# TAB 5: DATA EXPLORER
# =============================================================================

with tab5:
    st.markdown(f"<h3 style='color: {theme['text_primary']};'>Data Explorer</h3>", unsafe_allow_html=True)
    
    # Dataset selector
    dataset_option = st.selectbox(
        "Select Dataset to Explore",
        ["Orders", "Customers", "Restaurants", "Riders", "Delivery Events", "Order Items"]
    )
    
    # Display selected dataset
    if dataset_option == "Orders":
        display_df = filtered_orders[['order_id', 'customer_id', 'restaurant_name', 'order_datetime', 
                                       'order_status', 'gross_amount', 'discount_amount', 'net_amount',
                                       'payment_method', 'city', 'cuisine_type']].copy()
        st.markdown(f"**Showing {len(display_df):,} orders based on current filters**")
    elif dataset_option == "Customers":
        display_df = customers.copy()
        st.markdown(f"**Total customers: {len(display_df):,}**")
    elif dataset_option == "Restaurants":
        display_df = restaurants.copy()
        st.markdown(f"**Total restaurants: {len(display_df):,}**")
    elif dataset_option == "Riders":
        display_df = riders.copy()
        st.markdown(f"**Total riders: {len(display_df):,}**")
    elif dataset_option == "Delivery Events":
        display_df = delivery_events.copy()
        st.markdown(f"**Total delivery events: {len(display_df):,}**")
    else:
        display_df = order_items.copy()
        st.markdown(f"**Total order items: {len(display_df):,}**")
    
    # Search/Filter
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("🔍 Search", placeholder="Type to search...")
    with search_col2:
        rows_to_show = st.selectbox("Rows to display", [10, 25, 50, 100], index=1)
    
    # Apply search
    if search_term:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
    
    # Display dataframe
    st.dataframe(
        display_df.head(rows_to_show),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{dataset_option.lower().replace(' ', '_')}_export.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown(f"<h4 style='color: {theme['text_primary']};'>📊 Quick Statistics</h4>", unsafe_allow_html=True)
    
    if dataset_option == "Orders":
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Revenue", format_currency(display_df['net_amount'].sum()))
        with stat_col2:
            st.metric("Avg Order Value", f"AED {display_df['net_amount'].mean():.2f}")
        with stat_col3:
            st.metric("Total Discount", format_currency(display_df['discount_amount'].sum()))
    
    # Show data types and summary
    with st.expander("📋 Column Information"):
        col_info = pd.DataFrame({
            'Column': display_df.columns,
            'Data Type': display_df.dtypes.astype(str),
            'Non-Null Count': display_df.count().values,
            'Null Count': display_df.isnull().sum().values
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; padding: 20px; color: {theme["text_secondary"]};'>
        <p>🍔 <strong>BitesUAE Dashboard</strong> | Built with Streamlit & Plotly</p>
        <p style='font-size: 0.8rem;'>Data is synthetically generated for demonstration purposes</p>
    </div>
""", unsafe_allow_html=True)
