import pandas as pd
from sql_analysis import RestaurantAnalyzer

def generate_insights():
    """Generate business insights from Restaurant analytics data"""
    # Create analyzer
    analyzer = RestaurantAnalyzer()
    
    # Run all analyses
    results = analyzer.run_all_analyses()
    
    # Generate insights
    insights = []
    
    # 1. Peak Order Hours Insights
    peak_hours = results['peak_hours']
    busiest_hour = peak_hours.loc[peak_hours['order_count'].idxmax()]['order_hour']
    highest_value_hour = peak_hours.loc[peak_hours['avg_order_value'].idxmax()]['order_hour']
    
    insights.append(f"The busiest hour for orders is {int(busiest_hour)}:00, while the highest average order value occurs at {int(highest_value_hour)}:00.")
    
    lunch_orders = peak_hours[(peak_hours['order_hour'] >= 11) & (peak_hours['order_hour'] <= 14)]['order_count'].sum()
    dinner_orders = peak_hours[(peak_hours['order_hour'] >= 17) & (peak_hours['order_hour'] <= 21)]['order_count'].sum()
    total_orders = peak_hours['order_count'].sum()
    
    insights.append(f"Lunch hours (11:00-14:00) account for {lunch_orders/total_orders:.1%} of orders, while dinner hours (17:00-21:00) account for {dinner_orders/total_orders:.1%}.")
    
    # 2. Delivery Time Insights
    delivery_times = results['delivery_time_by_area']
    fastest_area = delivery_times.iloc[delivery_times['avg_delivery_time'].idxmin()]
    slowest_area = delivery_times.iloc[delivery_times['avg_delivery_time'].idxmax()]
    
    insights.append(f"The fastest delivery area is {fastest_area['area']} with an average delivery time of {fastest_area['avg_delivery_time']:.1f} minutes, while the slowest is {slowest_area['area']} with {slowest_area['avg_delivery_time']:.1f} minutes.")
    
    avg_late_pct = delivery_times['late_percentage'].mean()
    insights.append(f"On average, {avg_late_pct:.1f}% of deliveries are late (more than 5 minutes after the estimated time).")
    
    # 3. Popular Restaurant Insights
    popular_restaurants = results['popular_restaurants']
    top_restaurant = popular_restaurants.iloc[0]
    
    insights.append(f"The most popular restaurant is {top_restaurant['name']} ({top_restaurant['cuisine']}) with {int(top_restaurant['order_count'])} orders and ${top_restaurant['total_revenue']:,.2f} in revenue.")
    
    avg_restaurant_orders = popular_restaurants['order_count'].mean()
    insights.append(f"On average, each restaurant receives {avg_restaurant_orders:.1f} orders.")
    
    # 4. Customer Retention Insights
    customer_retention = results['customer_retention']
    vip_data = customer_retention[customer_retention['segment'] == 'VIP'].iloc[0]
    new_data = customer_retention[customer_retention['segment'] == 'New'].iloc[0]
    
    insights.append(f"VIP customers place {vip_data['avg_orders_per_customer']:.1f} orders on average and spend ${vip_data['avg_total_spent']:.2f}, compared to new customers who place {new_data['avg_orders_per_customer']:.1f} orders and spend ${new_data['avg_total_spent']:.2f}.")
    
    active_pct = customer_retention['active_last_30_days_pct'].mean()
    insights.append(f"On average, {active_pct:.1f}% of customers have been active in the last 30 days.")
    
    # 5. DashPass Impact Insights
    dashpass = results['dashpass_impact']
    dashpass_row = dashpass[dashpass['has_dashpass'] == 1].iloc[0]
    non_dashpass_row = dashpass[dashpass['has_dashpass'] == 0].iloc[0]
    
    order_diff = dashpass_row['orders_per_customer'] / non_dashpass_row['orders_per_customer'] - 1
    insights.append(f"DashPass subscribers place {order_diff:.0%} more orders than non-subscribers and spend ${dashpass_row['avg_order_value'] - non_dashpass_row['avg_order_value']:.2f} more per order on average.")
    
    fee_savings = non_dashpass_row['avg_delivery_fee'] - dashpass_row['avg_delivery_fee']
    insights.append(f"DashPass subscribers save an average of ${fee_savings:.2f} on delivery fees per order.")
    
    # 6. Driver Performance Insights
    driver_perf = results['driver_performance']
    fastest_vehicle = driver_perf.iloc[driver_perf['avg_delivery_time'].idxmin()]
    highest_rated = driver_perf.iloc[driver_perf['avg_rating'].idxmax()]
    
    insights.append(f"Drivers using {fastest_vehicle['vehicle_type']} have the fastest average delivery time at {fastest_vehicle['avg_delivery_time']:.1f} minutes.")
    insights.append(f"Drivers using {highest_rated['vehicle_type']} have the highest average rating at {highest_rated['avg_rating']:.1f} stars.")
    
    # 7. Cuisine Popularity Insights
    cuisines = results['popular_cuisines']
    top_cuisine = cuisines.iloc[0]
    highest_value_cuisine = cuisines.iloc[cuisines['avg_order_value'].idxmax()]
    
    insights.append(f"The most popular cuisine is {top_cuisine['cuisine']} with {int(top_cuisine['order_count'])} orders across {int(top_cuisine['restaurant_count'])} restaurants.")
    insights.append(f"The highest average order value is for {highest_value_cuisine['cuisine']} cuisine at ${highest_value_cuisine['avg_order_value']:.2f} per order.")
    
    # 8. Weekly Trends Insights
    weekly = results['weekly_trends']
    busiest_day_idx = weekly['order_count'].idxmax()
    busiest_day = weekly.loc[busiest_day_idx]['day_of_week']
    highest_value_day_idx = weekly['avg_order_value'].idxmax()
    highest_value_day = weekly.loc[highest_value_day_idx]['day_of_week']
    
    weekend_orders = weekly[weekly['day_of_week'].isin(['Saturday', 'Sunday'])]['order_count'].sum()
    weekday_orders = weekly[~weekly['day_of_week'].isin(['Saturday', 'Sunday'])]['order_count'].sum()
    
    insights.append(f"The busiest day of the week is {busiest_day} with {int(weekly.loc[busiest_day_idx]['order_count'])} orders.")
    insights.append(f"Weekend orders account for {weekend_orders/(weekend_orders+weekday_orders):.1%} of all orders.")
    
    # 9. Customer Frequency Insights
    frequency = results['customer_frequency']
    loyal_customers = frequency[frequency['order_count_bucket'] == '20+ orders'].iloc[0]
    
    insights.append(f"Highly loyal customers (20+ orders) spend an average of ${loyal_customers['avg_total_spent']:.2f} and have an average order value of ${loyal_customers['avg_order_value']:.2f}.")
    
    # 10. Delivery Issues Insights
    issues = results['delivery_issues']
    top_issue = issues.iloc[0]
    
    insights.append(f"The most common delivery issue is '{top_issue['issue_reported']}' with {int(top_issue['issue_count'])} occurrences and an average rating of {top_issue['avg_rating']:.1f} stars.")
    
    # Close connection
    analyzer.close()
    
    return insights

def print_insights():
    """Print insights in a formatted way"""
    insights = generate_insights()
    
    print("\n" + "="*80)
    print(" "*30 + "KEY BUSINESS INSIGHTS")
    print("="*80)
    
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")
    
    print("="*80)

if __name__ == "__main__":
    print_insights()