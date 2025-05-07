import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import os

# Set page configuration
st.set_page_config(
    page_title="Restaurant Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF3008;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #FF3008;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8F8F8;
        border-radius: 5px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FF3008;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Fix for SQLite threading issues
class ThreadSafeRestaurantAnalyzer:
    def __init__(self, db_path='Restaurant_analytics.db'):
        """Initialize the analyzer without opening a connection"""
        self.db_path = db_path
    
    def execute_query(self, query):
        """Execute SQL query in a thread-safe way"""
        # Create a new connection for each query
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()
    
    def get_cuisines(self):
        """Get all unique cuisines"""
        return self.execute_query("SELECT DISTINCT cuisine FROM restaurants ORDER BY cuisine")
    
    def get_date_range(self):
        """Get min and max dates from orders"""
        return self.execute_query("SELECT MIN(order_date) as min_date, MAX(order_date) as max_date FROM orders")
    
    def get_kpi_metrics(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get KPI metrics"""
        query = f"""
        SELECT 
            COUNT(DISTINCT o.order_id) as total_orders,
            COUNT(DISTINCT o.customer_id) as total_customers,
            ROUND(SUM(o.total), 2) as total_revenue,
            ROUND(AVG(o.total), 2) as avg_order_value,
            ROUND(AVG(d.delivery_duration_minutes), 2) as avg_delivery_time,
            ROUND(SUM(CASE WHEN d.is_late = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as late_percentage
        FROM orders o
        LEFT JOIN deliveries d ON o.order_id = d.order_id
        WHERE o.status = 'Completed'
        AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        # Add cuisine filter if selected
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND o.restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
        
        return self.execute_query(query)

    def get_order_trends(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get order trends over time"""
        query = f"""
        SELECT 
            strftime('%Y-%m', order_date) as month,
            COUNT(order_id) as order_count,
            ROUND(SUM(total), 2) as total_revenue,
            ROUND(AVG(total), 2) as avg_order_value
        FROM orders
        WHERE status = 'Completed'
        AND order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        # Add cuisine filter if selected
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
        
        query += "GROUP BY month ORDER BY month"
        
        return self.execute_query(query)

    def get_peak_hours(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get peak order hours"""
        query = f"""
        SELECT 
            order_hour,
            COUNT(*) as order_count,
            ROUND(AVG(total), 2) as avg_order_value
        FROM orders
        WHERE status = 'Completed'
        AND order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
            
        query += "GROUP BY order_hour ORDER BY order_hour"
        
        return self.execute_query(query)

    def get_weekly_patterns(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get weekly order patterns"""
        query = f"""
        SELECT 
            day_of_week,
            COUNT(*) as order_count,
            ROUND(AVG(total), 2) as avg_order_value
        FROM orders
        WHERE status = 'Completed'
        AND order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
            
        query += """
        GROUP BY day_of_week
        ORDER BY 
            CASE 
                WHEN day_of_week = 'Monday' THEN 1
                WHEN day_of_week = 'Tuesday' THEN 2
                WHEN day_of_week = 'Wednesday' THEN 3
                WHEN day_of_week = 'Thursday' THEN 4
                WHEN day_of_week = 'Friday' THEN 5
                WHEN day_of_week = 'Saturday' THEN 6
                WHEN day_of_week = 'Sunday' THEN 7
            END
        """
        
        return self.execute_query(query)

    def get_price_range_analysis(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get performance by price range"""
        query = f"""
        SELECT 
            r.price_range,
            COUNT(o.order_id) as order_count,
            ROUND(SUM(o.total), 2) as total_revenue,
            ROUND(AVG(o.total), 2) as avg_order_value,
            COUNT(DISTINCT r.restaurant_id) as restaurant_count,
            ROUND(AVG(o.tip), 2) as avg_tip
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        WHERE o.status = 'Completed'
        AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND r.cuisine IN ('{cuisine_list}')
            """
            
        query += """
        GROUP BY r.price_range
        ORDER BY 
            CASE 
                WHEN r.price_range = '$' THEN 1
                WHEN r.price_range = '$$' THEN 2
                WHEN r.price_range = '$$$' THEN 3
                WHEN r.price_range = '$$$$' THEN 4
            END
        """
        
        return self.execute_query(query)
        
    def get_popular_restaurants(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get most popular restaurants by order count and revenue"""
        query = f"""
        SELECT 
            r.restaurant_id,
            r.name,
            r.cuisine,
            r.price_range,
            r.rating,
            COUNT(o.order_id) as order_count,
            SUM(o.total) as total_revenue,
            AVG(o.total) as avg_order_value,
            SUM(o.tip) as total_tips,
            AVG(o.tip) as avg_tip
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        WHERE o.status = 'Completed'
        AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND r.cuisine IN ('{cuisine_list}')
            """
            
        query += """
        GROUP BY r.restaurant_id, r.name, r.cuisine, r.price_range, r.rating
        ORDER BY order_count DESC
        LIMIT 15
        """
        
        return self.execute_query(query)
            
    def get_popular_cuisines(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get most popular cuisines"""
        query = f"""
        SELECT 
            r.cuisine,
            COUNT(o.order_id) as order_count,
            SUM(o.total) as total_revenue,
            AVG(o.total) as avg_order_value,
            COUNT(DISTINCT r.restaurant_id) as restaurant_count
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        WHERE o.status = 'Completed'
        AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND r.cuisine IN ('{cuisine_list}')
            """
            
        query += """
        GROUP BY r.cuisine
        ORDER BY order_count DESC
        LIMIT 15
        """
        
        return self.execute_query(query)

    def get_area_delivery(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get delivery performance by area"""
        query = f"""
        SELECT 
            r.area,
            COUNT(d.delivery_id) as delivery_count,
            ROUND(AVG(d.delivery_duration_minutes), 2) as avg_delivery_time,
            ROUND(AVG(d.delivery_delay_minutes), 2) as avg_delay,
            ROUND(SUM(CASE WHEN d.is_late = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as late_percentage
        FROM deliveries d
        JOIN orders o ON d.order_id = o.order_id
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE o.status = 'Completed'
        AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND r.cuisine IN ('{cuisine_list}')
            """
            
        query += "GROUP BY r.area ORDER BY avg_delivery_time DESC"
        
        return self.execute_query(query)

    def get_driver_performance(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get driver performance metrics"""
        query = f"""
        SELECT 
            dr.vehicle_type,
            COUNT(DISTINCT dr.driver_id) as driver_count,
            COUNT(d.delivery_id) as delivery_count,
            ROUND(COUNT(d.delivery_id) * 1.0 / COUNT(DISTINCT dr.driver_id), 2) as deliveries_per_driver,
            ROUND(AVG(d.delivery_duration_minutes), 2) as avg_delivery_time,
            ROUND(AVG(d.customer_rating), 2) as avg_rating,
            ROUND(SUM(CASE WHEN d.is_late = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as late_percentage
        FROM drivers dr
        JOIN deliveries d ON dr.driver_id = d.driver_id
        JOIN orders o ON d.order_id = o.order_id
        WHERE o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND o.restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
            
        query += "GROUP BY dr.vehicle_type ORDER BY avg_delivery_time"
        
        return self.execute_query(query)

    def get_delivery_issues(self, start_date_str, end_date_str, selected_cuisines=None):
        """Get delivery issues analysis"""
        query = f"""
        SELECT 
            issue_reported,
            COUNT(*) as issue_count,
            ROUND(AVG(customer_rating), 2) as avg_rating,
            ROUND(AVG(delivery_delay_minutes), 2) as avg_delay
        FROM deliveries d
        JOIN orders o ON d.order_id = o.order_id
        WHERE issue_reported IS NOT NULL
        AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        if selected_cuisines and len(selected_cuisines) > 0:
            cuisine_list = "', '".join(selected_cuisines)
            query += f"""
            AND o.restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
            
        query += "GROUP BY issue_reported ORDER BY issue_count DESC"
        
        return self.execute_query(query)

# Initialize the thread-safe analyzer
@st.cache_resource
def get_analyzer():
    return ThreadSafeRestaurantAnalyzer()

# Function to show Orders Analysis tab
def show_orders_analysis(analyzer, start_date_str, end_date_str, selected_cuisines):
    st.markdown('<div class="section-header">Order Trends</div>', unsafe_allow_html=True)
    
    # Order trends over time
    order_trends = analyzer.get_order_trends(start_date_str, end_date_str, selected_cuisines)
    
    if not order_trends.empty:
        # Create a plotly figure with dual y-axis
        fig = sp.make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add order count line
        fig.add_trace(
            go.Scatter(
                x=order_trends['month'],
                y=order_trends['order_count'],
                name="Order Count",
                line=dict(color="#FF3008", width=3)
            ),
            secondary_y=False
        )
        
        # Add revenue bars
        fig.add_trace(
            go.Bar(
                x=order_trends['month'],
                y=order_trends['total_revenue'],
                name="Total Revenue",
                marker_color="rgba(75, 192, 192, 0.7)"
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title="Monthly Order Trends",
            xaxis_title="Month",
            legend=dict(x=0, y=1.1, orientation="h")
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Order Count", secondary_y=False)
        fig.update_yaxes(title_text="Total Revenue ($)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Peak order hours analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Peak Order Hours")
        
        peak_hours = analyzer.get_peak_hours(start_date_str, end_date_str, selected_cuisines)
        
        if not peak_hours.empty:
            fig = px.bar(
                peak_hours, 
                x="order_hour", 
                y="order_count",
                labels={"order_hour": "Hour of Day", "order_count": "Number of Orders"},
                title="Orders by Hour of Day",
                color_discrete_sequence=["#FF3008"]
            )
            
            # Add hour labels (convert to 12-hour format)
            hour_labels = {h: f"{h%12 if h%12 else 12} {'AM' if h<12 else 'PM'}" for h in range(24)}
            fig.update_xaxes(tickvals=list(range(24)), ticktext=list(hour_labels.values()))
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Weekly Order Patterns")
        
        weekly_patterns = analyzer.get_weekly_patterns(start_date_str, end_date_str, selected_cuisines)
        
        if not weekly_patterns.empty:
            fig = px.bar(
                weekly_patterns, 
                x="day_of_week", 
                y="order_count",
                labels={"day_of_week": "Day of Week", "order_count": "Number of Orders"},
                title="Orders by Day of Week",
                color="day_of_week",
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Function to show Customer Analysis tab
def show_customer_analysis(analyzer, start_date_str, end_date_str, selected_cuisines):
    st.markdown('<div class="section-header">Customer Insights</div>', unsafe_allow_html=True)
    
    st.subheader("Performance by Price Range")

    price_analysis = analyzer.get_price_range_analysis(start_date_str, end_date_str, selected_cuisines)
    
    if not price_analysis.empty:
        # Create three columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Order distribution by price range
            fig = px.pie(
                price_analysis,
                values='order_count',
                names='price_range',
                title='Order Distribution by Price Range',
                color_discrete_sequence=px.colors.sequential.Greens
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Average order value by price range
            fig = px.bar(
                price_analysis,
                x='price_range',
                y='avg_order_value',
                title='Average Order Value by Price Range',
                labels={'price_range': 'Price Range', 'avg_order_value': 'Average Order Value ($)'},
                color='price_range',
                color_discrete_sequence=px.colors.sequential.Greens
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Average tip by price range
            fig = px.bar(
                price_analysis,
                x='price_range',
                y='avg_tip',
                title='Average Tip by Price Range',
                labels={'price_range': 'Price Range', 'avg_tip': 'Average Tip ($)'},
                color='price_range',
                color_discrete_sequence=px.colors.sequential.Greens
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Function to show Restaurant Analysis tab
def show_restaurant_analysis(analyzer, start_date_str, end_date_str, selected_cuisines):
    st.markdown('<div class="section-header">Restaurant Analysis</div>', unsafe_allow_html=True)
    
    # Popular Restaurants
    st.subheader("Most Popular Restaurants")
    
    # Use the correct method name 'get_popular_restaurants' with underscores
    popular_restaurants = analyzer.get_popular_restaurants(start_date_str, end_date_str, selected_cuisines)
    
    if not popular_restaurants.empty:
        # Create bar chart of popular restaurants
        fig = px.bar(
            popular_restaurants.head(10),  # Show top 10 restaurants
            y='name',
            x='order_count',
            orientation='h',
            color='rating',
            hover_data=['cuisine', 'price_range', 'total_revenue', 'avg_order_value'],
            title='Top 10 Most Popular Restaurants by Order Count',
            labels={'name': 'Restaurant', 'order_count': 'Number of Orders', 'rating': 'Rating'},
            color_continuous_scale='RdYlGn',
            text='rating'
        )
        fig.update_traces(texttemplate='%{text}★', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
        
    # Popular Cuisines
    st.subheader("Most Popular Cuisines")
    
    popular_cuisines = analyzer.get_popular_cuisines(start_date_str, end_date_str, selected_cuisines)
    
    if not popular_cuisines.empty:
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of cuisine distribution
            fig = px.pie(
                popular_cuisines,
                values='order_count',
                names='cuisine',
                title='Order Distribution by Cuisine',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Average order value by cuisine
            fig = px.bar(
                popular_cuisines.head(10),  # Top 10 cuisines
                x='cuisine',
                y='avg_order_value',
                color='restaurant_count',
                title='Average Order Value by Cuisine',
                labels={
                    'cuisine': 'Cuisine', 
                    'avg_order_value': 'Average Order Value ($)',
                    'restaurant_count': 'Number of Restaurants'
                },
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Restaurant Performance Metrics
    st.subheader("Restaurant Performance Analysis")
    
    if not popular_restaurants.empty:
        # Create scatter plot comparing different performance metrics
        fig = px.scatter(
            popular_restaurants,
            x='avg_order_value',
            y='avg_tip',
            size='order_count',
            color='rating',
            hover_name='name',
            hover_data=['cuisine', 'price_range', 'total_revenue'],
            title='Restaurant Performance Comparison',
            labels={
                'avg_order_value': 'Average Order Value ($)',
                'avg_tip': 'Average Tip ($)',
                'order_count': 'Total Orders',
                'rating': 'Rating'
            },
            color_continuous_scale='RdYlGn'
        )
        
        # Add a trendline
        fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(coloraxis_colorbar=dict(title='Rating'))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table with restaurant details
        st.subheader("Restaurant Details")
        
        # Format the data for display
        display_data = popular_restaurants.copy()
        display_data['total_revenue'] = display_data['total_revenue'].map('${:,.2f}'.format)
        display_data['avg_order_value'] = display_data['avg_order_value'].map('${:.2f}'.format)
        display_data['avg_tip'] = display_data['avg_tip'].map('${:.2f}'.format)
        display_data['total_tips'] = display_data['total_tips'].map('${:,.2f}'.format)
        display_data['rating'] = display_data['rating'].map('{:.1f}★'.format)
        
        # Select only the columns we want to display
        display_columns = ['name', 'cuisine', 'price_range', 'rating', 
                          'order_count', 'total_revenue', 'avg_order_value', 'avg_tip']
        
        st.dataframe(
            display_data[display_columns],
            column_config={
                "name": "Restaurant Name",
                "cuisine": "Cuisine",
                "price_range": "Price Range",
                "rating": "Rating",
                "order_count": "Order Count",
                "total_revenue": "Total Revenue",
                "avg_order_value": "Avg Order Value",
                "avg_tip": "Avg Tip"
            },
            use_container_width=True
        )
        
# Function to show Delivery Analysis tab
def show_delivery_analysis(analyzer, start_date_str, end_date_str, selected_cuisines):
    st.markdown('<div class="section-header">Delivery Analysis</div>', unsafe_allow_html=True)
    
    # Delivery times by area
    st.subheader("Delivery Performance by Area")
    
    area_delivery = analyzer.get_area_delivery(start_date_str, end_date_str, selected_cuisines)
    
    if not area_delivery.empty:
        # Sort by delivery time
        area_delivery = area_delivery.sort_values('avg_delivery_time')
        
        fig = px.bar(
            area_delivery,
            y='area',
            x='avg_delivery_time',
            orientation='h',
            color='late_percentage',
            hover_data=['delivery_count', 'avg_delay'],
            title='Average Delivery Time by Area',
            labels={'area': 'Area', 'avg_delivery_time': 'Average Delivery Time (minutes)', 'late_percentage': 'Late %'},
            color_continuous_scale='Reds'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Driver performance
    st.subheader("Driver Performance")
    
    driver_performance = analyzer.get_driver_performance(start_date_str, end_date_str, selected_cuisines)
    
    if not driver_performance.empty:
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Average delivery time by vehicle type
            fig = px.bar(
                driver_performance,
                x='vehicle_type',
                y='avg_delivery_time',
                title='Average Delivery Time by Vehicle Type',
                labels={'vehicle_type': 'Vehicle Type', 'avg_delivery_time': 'Average Delivery Time (minutes)'},
                color='vehicle_type',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating vs. late percentage
            fig = px.scatter(
                driver_performance,
                x='late_percentage',
                y='avg_rating',
                size='delivery_count',
                color='vehicle_type',
                hover_data=['deliveries_per_driver', 'driver_count'],
                title='Driver Rating vs. Late Percentage',
                labels={
                    'late_percentage': 'Late Percentage (%)',
                    'avg_rating': 'Average Rating',
                    'delivery_count': 'Delivery Count'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Delivery issues
    st.subheader("Delivery Issues Analysis")
    
    delivery_issues = analyzer.get_delivery_issues(start_date_str, end_date_str, selected_cuisines)
    
    if not delivery_issues.empty and len(delivery_issues) > 0:
        fig = px.bar(
            delivery_issues,
            y='issue_reported',
            x='issue_count',
            orientation='h',
            color='avg_rating',
            hover_data=['avg_delay'],
            title='Delivery Issues by Type',
            labels={'issue_reported': 'Issue Type', 'issue_count': 'Count', 'avg_rating': 'Avg Rating'},
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivery issues found for the selected filters.")

# Main function
def main():
    # Header
    st.markdown('<div class="main-header">🍔 Restaurant Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Get the analyzer
    analyzer = get_analyzer()
    
    # Cuisine filter for sidebar
    cuisines_df = analyzer.get_cuisines()
    cuisines = cuisines_df['cuisine'].tolist()
    selected_cuisines = st.sidebar.multiselect("Select Cuisines", cuisines, default=None)
    
    # Add a date range filter in sidebar
    st.sidebar.subheader("Date Range")
    
    # Get min and max dates from orders
    date_range_df = analyzer.get_date_range()
    min_date = pd.to_datetime(date_range_df['min_date'].iloc[0])
    max_date = pd.to_datetime(date_range_df['max_date'].iloc[0])
    
    # Create date range selector
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    
    # Convert to strings for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Top metrics
    st.markdown('<div class="section-header">Key Performance Metrics</div>', unsafe_allow_html=True)
    
    # Get KPI metrics with date filter
    kpi_metrics = analyzer.get_kpi_metrics(start_date_str, end_date_str, selected_cuisines)
    
    # Display metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{int(kpi_metrics["total_orders"].iloc[0])}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Orders</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${kpi_metrics["total_revenue"].iloc[0]:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Revenue</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${kpi_metrics["avg_order_value"].iloc[0]:.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Avg Order Value</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{kpi_metrics["avg_delivery_time"].iloc[0]:.1f} min</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Avg Delivery Time</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('---')
    
    # Create radio buttons for tab selection instead of using st.tabs
    tab_selected = st.radio(
        "Select Analysis",
        ["Orders Analysis", "Customer Analysis", "Restaurant Analysis", "Delivery Analysis"],
        horizontal=True
    )
    
    # Based on the selected tab, show the appropriate content
    if tab_selected == "Orders Analysis":
        show_orders_analysis(analyzer, start_date_str, end_date_str, selected_cuisines)
    elif tab_selected == "Customer Analysis":
        show_customer_analysis(analyzer, start_date_str, end_date_str, selected_cuisines)
    elif tab_selected == "Restaurant Analysis":
        show_restaurant_analysis(analyzer, start_date_str, end_date_str, selected_cuisines)
    elif tab_selected == "Delivery Analysis":
        show_delivery_analysis(analyzer, start_date_str, end_date_str, selected_cuisines)

if __name__ == "__main__":
    main()