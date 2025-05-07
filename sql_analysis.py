# sql_analysis.py
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

class RestaurantAnalyzer:
    def __init__(self, db_path='Restaurant_analytics.db'):
        """Initialize the analyzer with database connection"""
        self.conn = sqlite3.connect(db_path)
        self.engine = create_engine(f'sqlite:///{db_path}')
    
    def execute_query(self, query):
        """Execute SQL query and return results as DataFrame"""
        return pd.read_sql_query(query, self.conn)
    
    def peak_order_hours(self):
        """Analyze peak order hours"""
        query = """
        SELECT 
            order_hour,
            COUNT(*) as order_count,
            AVG(total) as avg_order_value,
            SUM(total) as total_revenue
        FROM orders
        WHERE status = 'Completed'
        GROUP BY order_hour
        ORDER BY order_count DESC
        """
        return self.execute_query(query)
    
    def delivery_time_by_area(self):
        """Analyze average delivery time by area"""
        query = """
        SELECT 
            r.area,
            COUNT(d.delivery_id) as delivery_count,
            AVG(d.delivery_duration_minutes) as avg_delivery_time,
            AVG(d.delivery_delay_minutes) as avg_delay,
            SUM(CASE WHEN d.is_late = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as late_percentage
        FROM deliveries d
        JOIN orders o ON d.order_id = o.order_id
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        GROUP BY r.area
        ORDER BY avg_delivery_time DESC
        """
        return self.execute_query(query)
    
    def popular_restaurants(self):
        """Find most popular restaurants by order count and revenue"""
        query = """
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
        GROUP BY r.restaurant_id, r.name, r.cuisine, r.price_range, r.rating
        ORDER BY order_count DESC
        LIMIT 20
        """
        return self.execute_query(query)
    
    def customer_retention(self):
        """Analyze customer retention metrics"""
        query = """
        SELECT 
            c.segment,
            COUNT(DISTINCT c.customer_id) as customer_count,
            AVG(c.order_count) as avg_orders_per_customer,
            AVG(c.total_spent) as avg_total_spent,
            AVG(c.customer_lifetime_days) as avg_lifetime_days,
            SUM(CASE WHEN c.days_since_last_order <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as active_last_30_days_pct
        FROM customers c
        GROUP BY c.segment
        ORDER BY avg_total_spent DESC
        """
        return self.execute_query(query)
    
    def dashpass_impact(self):
        """Analyze the impact of DashPass subscriptions"""
        query = """
        SELECT 
            c.has_dashpass,
            COUNT(DISTINCT c.customer_id) as customer_count,
            COUNT(o.order_id) as order_count,
            COUNT(o.order_id) * 1.0 / COUNT(DISTINCT c.customer_id) as orders_per_customer,
            AVG(o.total) as avg_order_value,
            AVG(o.delivery_fee) as avg_delivery_fee,
            SUM(o.total) as total_revenue
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status = 'Completed'
        GROUP BY c.has_dashpass
        """
        return self.execute_query(query)
    
    def driver_performance(self):
        """Analyze driver performance metrics"""
        query = """
        SELECT 
            dr.vehicle_type,
            COUNT(DISTINCT dr.driver_id) as driver_count,
            COUNT(d.delivery_id) as delivery_count,
            COUNT(d.delivery_id) * 1.0 / COUNT(DISTINCT dr.driver_id) as deliveries_per_driver,
            AVG(d.delivery_duration_minutes) as avg_delivery_time,
            AVG(d.customer_rating) as avg_rating,
            SUM(CASE WHEN d.is_late = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as late_percentage
        FROM drivers dr
        JOIN deliveries d ON dr.driver_id = d.driver_id
        GROUP BY dr.vehicle_type
        ORDER BY avg_delivery_time
        """
        return self.execute_query(query)
    
    def most_popular_cuisines(self):
        """Analyze most popular cuisines by order count and revenue"""
        query = """
        SELECT 
            r.cuisine,
            COUNT(o.order_id) as order_count,
            SUM(o.total) as total_revenue,
            AVG(o.total) as avg_order_value,
            COUNT(DISTINCT r.restaurant_id) as restaurant_count
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        WHERE o.status = 'Completed'
        GROUP BY r.cuisine
        ORDER BY order_count DESC
        """
        return self.execute_query(query)
    
    def weekly_order_trends(self):
        """Analyze weekly order trends"""
        query = """
        SELECT 
            day_of_week,
            COUNT(*) as order_count,
            AVG(total) as avg_order_value,
            SUM(total) as total_revenue
        FROM orders
        WHERE status = 'Completed'
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
    
    def delivery_issues_analysis(self):
        """Analyze delivery issues"""
        query = """
        SELECT 
            issue_reported,
            COUNT(*) as issue_count,
            AVG(customer_rating) as avg_rating,
            AVG(delivery_delay_minutes) as avg_delay
        FROM deliveries
        WHERE issue_reported IS NOT NULL
        GROUP BY issue_reported
        ORDER BY issue_count DESC
        """
        return self.execute_query(query)
    
    def customer_order_frequency(self):
        """Analyze customer order frequency"""
        query = """
        SELECT 
            order_count_bucket,
            COUNT(*) as customer_count,
            AVG(avg_order_value) as avg_order_value,
            AVG(total_spent) as avg_total_spent
        FROM (
            SELECT 
                customer_id,
                CASE 
                    WHEN order_count = 1 THEN '1 order'
                    WHEN order_count BETWEEN 2 AND 5 THEN '2-5 orders'
                    WHEN order_count BETWEEN 6 AND 10 THEN '6-10 orders'
                    WHEN order_count BETWEEN 11 AND 20 THEN '11-20 orders'
                    ELSE '20+ orders'
                END as order_count_bucket,
                avg_order_value,
                total_spent
            FROM customers
        )
        GROUP BY order_count_bucket
        ORDER BY 
            CASE 
                WHEN order_count_bucket = '1 order' THEN 1
                WHEN order_count_bucket = '2-5 orders' THEN 2
                WHEN order_count_bucket = '6-10 orders' THEN 3
                WHEN order_count_bucket = '11-20 orders' THEN 4
                WHEN order_count_bucket = '20+ orders' THEN 5
            END
        """
        return self.execute_query(query)
    
    def run_all_analyses(self):
        """Run all analyses and return results as a dictionary"""
        results = {
            'peak_hours': self.peak_order_hours(),
            'delivery_time_by_area': self.delivery_time_by_area(),
            'popular_restaurants': self.popular_restaurants(),
            'customer_retention': self.customer_retention(),
            'dashpass_impact': self.dashpass_impact(),
            'driver_performance': self.driver_performance(),
            'popular_cuisines': self.most_popular_cuisines(),
            'weekly_trends': self.weekly_order_trends(),
            'delivery_issues': self.delivery_issues_analysis(),
            'customer_frequency': self.customer_order_frequency()
        }
        
        return results
    
    def close(self):
        """Close database connection"""
        self.conn.close()


# This function allows for filtering in the StreamLit app
def filter_by_date_and_cuisine(analyzer, query, start_date_str=None, end_date_str=None, selected_cuisines=None):
    """
    Add date and cuisine filters to a SQL query
    
    Args:
        analyzer: RestaurantAnalyzer instance
        query: Base SQL query string
        start_date_str: Optional start date string in 'YYYY-MM-DD' format
        end_date_str: Optional end date string in 'YYYY-MM-DD' format
        selected_cuisines: Optional list of cuisine names
    
    Returns:
        DataFrame with query results
    """
    filtered_query = query
    
    # Add date filter if provided
    if start_date_str and end_date_str:
        if "WHERE" in filtered_query:
            filtered_query += f" AND o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'"
        else:
            filtered_query += f" WHERE o.order_date BETWEEN '{start_date_str}' AND '{end_date_str}'"
    
    # Add cuisine filter if provided
    if selected_cuisines and len(selected_cuisines) > 0:
        cuisine_list = "', '".join(selected_cuisines)
        if "WHERE" in filtered_query:
            filtered_query += f"""
            AND o.restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
        else:
            filtered_query += f"""
            WHERE o.restaurant_id IN (
                SELECT restaurant_id FROM restaurants
                WHERE cuisine IN ('{cuisine_list}')
            )
            """
    
    return analyzer.execute_query(filtered_query)


if __name__ == "__main__":
    # Create analyzer
    analyzer = RestaurantAnalyzer()
    
    # Run all analyses
    results = analyzer.run_all_analyses()
    
    # Print results
    for name, df in results.items():
        print(f"\n=== {name} ===")
        print(df.head())
    
    # Close connection
    analyzer.close()