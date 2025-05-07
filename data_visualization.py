import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sql_analysis import RestaurantAnalyzer

def set_plotting_style():
    """Set plotting style for consistent visualizations"""
    plt.style.use('fivethirtyeight')
    sns.set_palette('colorblind')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

def plot_peak_order_hours(peak_hours_df):
    """Plot peak order hours"""
    plt.figure(figsize=(14, 8))
    
    # Create subplots
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Plot order count bars
    bars = ax1.bar(peak_hours_df['order_hour'], peak_hours_df['order_count'], color='royalblue', alpha=0.7)
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Number of Orders', color='royalblue')
    ax1.tick_params(axis='y', labelcolor='royalblue')
    
    # Add a second y-axis for average order value
    ax2 = ax1.twinx()
    line = ax2.plot(peak_hours_df['order_hour'], peak_hours_df['avg_order_value'], 'r-', linewidth=3, label='Average Order Value')
    ax2.set_ylabel('Average Order Value ($)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # Set x-ticks to show all hours
    ax1.set_xticks(range(0, 24))
    ax1.set_xticklabels([f"{h}:00" for h in range(0, 24)], rotation=45)
    
    # Highlight key meal times
    meal_times = {
        'Breakfast': (7, 9),
        'Lunch': (11, 13),
        'Dinner': (17, 20),
        'Late Night': (22, 23)
    }
    
    for meal, (start, end) in meal_times.items():
        plt.axvspan(start-0.5, end+0.5, alpha=0.2, color='gray')
        plt.text((start+end)/2, max(peak_hours_df['order_count'])*0.9, meal, 
                 ha='center', va='center', fontsize=12, color='black',
                 bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    # Add title and grid
    plt.title('Peak Order Hours and Average Order Value by Hour of Day', fontsize=18)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add annotations for the peak hours
    top_hours = peak_hours_df.nlargest(3, 'order_count')
    for _, row in top_hours.iterrows():
        ax1.annotate(f"{int(row['order_count'])} orders",
                    xy=(row['order_hour'], row['order_count']),
                    xytext=(0, 20),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    color='black',
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('visualizations/peak_order_hours.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_delivery_time_by_area(delivery_time_df):
    """Plot delivery time by area"""
    plt.figure(figsize=(14, 8))
    
    # Sort by average delivery time
    delivery_time_df = delivery_time_df.sort_values('avg_delivery_time')
    
    # Create a horizontal bar chart
    bars = plt.barh(delivery_time_df['area'], delivery_time_df['avg_delivery_time'], 
                   color='teal', alpha=0.7)
    
    # Add delivery count as text labels
    for i, (_, row) in enumerate(delivery_time_df.iterrows()):
        plt.text(row['avg_delivery_time'] + 1, i, 
                f"n={int(row['delivery_count'])} ({row['late_percentage']:.1f}% late)", 
                va='center', fontsize=10)
    
    # Customize plot
    plt.xlabel('Average Delivery Time (minutes)')
    plt.ylabel('Area')
    plt.title('Average Delivery Time by Area', fontsize=18)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add color-coded indicators for late percentages
    for i, (_, row) in enumerate(delivery_time_df.iterrows()):
        if row['late_percentage'] > 20:
            color = 'red'
        elif row['late_percentage'] > 10:
            color = 'orange'
        else:
            color = 'green'
        
        plt.plot([0], [i], marker='o', markersize=10, color=color)
    
    # Add a legend for the late percentage indicators
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='<10% Late'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='10-20% Late'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='>20% Late')
    ]
    plt.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig('visualizations/delivery_time_by_area.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_popular_restaurants(popular_restaurants_df):
    """Plot most popular restaurants"""
    plt.figure(figsize=(14, 10))
    
    # Take top 15 restaurants for better readability
    top_restaurants = popular_restaurants_df.head(15)
    
    # Create a horizontal bar chart for order count
    bars = plt.barh(top_restaurants['name'], top_restaurants['order_count'], 
                   color='royalblue', alpha=0.7)
    
    # Add cuisine and rating information as text labels
    # FIX: Escape dollar signs in text to prevent MathText parsing errors
    for i, (_, row) in enumerate(top_restaurants.iterrows()):
        # Escape dollar signs with backslash
        price_range_escaped = row['price_range'].replace('$', r'\$')
        plt.text(row['order_count'] + 5, i, 
                f"{row['cuisine']} ({price_range_escaped}) - {row['rating']}★", 
                va='center')
    
    # Customize plot
    plt.xlabel('Number of Orders')
    plt.ylabel('Restaurant')
    plt.title('Top 15 Most Popular Restaurants by Order Count', fontsize=18)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('visualizations/popular_restaurants.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_customer_retention(customer_retention_df):
    """Plot customer retention metrics by segment"""
    plt.figure(figsize=(14, 8))
    
    # Create subplots
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Sort by average total spent
    customer_retention_df = customer_retention_df.sort_values('avg_total_spent')
    
    # Set x positions for bars
    x = np.arange(len(customer_retention_df))
    width = 0.35
    
    # Plot average orders per customer bars
    bars1 = ax1.bar(x - width/2, customer_retention_df['avg_orders_per_customer'], 
                   width, color='royalblue', alpha=0.7, label='Avg Orders per Customer')
    ax1.set_ylabel('Average Orders per Customer', color='royalblue')
    ax1.tick_params(axis='y', labelcolor='royalblue')
    
    # Add a second y-axis for average total spent
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, customer_retention_df['avg_total_spent'], 
                   width, color='green', alpha=0.7, label='Avg Total Spent')
    ax2.set_ylabel('Average Total Spent ($)', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    
    # Set x-axis ticks and labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(customer_retention_df['segment'])
    
    # Add customer count and active percentage as text labels
    for i, (_, row) in enumerate(customer_retention_df.iterrows()):
        ax1.text(i, row['avg_orders_per_customer'] + 0.5, 
                f"n={int(row['customer_count'])}", 
                ha='center', va='bottom', fontsize=10, color='blue')
        
        ax2.text(i, row['avg_total_spent'] + 20, 
                f"{row['active_last_30_days_pct']:.1f}% active", 
                ha='center', va='bottom', fontsize=10, color='darkgreen')
    
    # Add title and grid
    plt.title('Customer Metrics by Segment', fontsize=18)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add a legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig('visualizations/customer_retention.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_dashpass_impact(dashpass_df):
    """Plot impact of DashPass subscriptions"""
    plt.figure(figsize=(14, 10))
    
    # Create subplots in a 2x2 grid
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    
    # Convert boolean to string for better labels
    dashpass_df['membership'] = dashpass_df['has_dashpass'].map({1: 'DashPass', 0: 'Non-DashPass'})
    
    # Plot 1: Orders per customer
    axs[0, 0].bar(dashpass_df['membership'], dashpass_df['orders_per_customer'], 
                 color=['orange', 'purple'])
    axs[0, 0].set_title('Orders per Customer')
    axs[0, 0].set_ylabel('Average Orders')
    axs[0, 0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot 2: Average order value
    axs[0, 1].bar(dashpass_df['membership'], dashpass_df['avg_order_value'], 
                 color=['orange', 'purple'])
    axs[0, 1].set_title('Average Order Value')
    axs[0, 1].set_ylabel('Amount ($)')
    axs[0, 1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot 3: Average delivery fee
    axs[1, 0].bar(dashpass_df['membership'], dashpass_df['avg_delivery_fee'], 
                 color=['orange', 'purple'])
    axs[1, 0].set_title('Average Delivery Fee')
    axs[1, 0].set_ylabel('Amount ($)')
    axs[1, 0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot 4: Customer count vs. order count
    width = 0.35
    x = np.arange(len(dashpass_df))
    
    # Normalize values for better visualization
    max_count = max(dashpass_df['customer_count'].max(), dashpass_df['order_count'].max())
    normalized_customer_count = dashpass_df['customer_count'] / max_count * 100
    normalized_order_count = dashpass_df['order_count'] / max_count * 100
    
    axs[1, 1].bar(x - width/2, normalized_customer_count, width, label='Customer %', 
                 color='orange', alpha=0.7)
    axs[1, 1].bar(x + width/2, normalized_order_count, width, label='Order %', 
                 color='purple', alpha=0.7)
    axs[1, 1].set_title('Customer vs. Order Distribution')
    axs[1, 1].set_ylabel('Percentage')
    axs[1, 1].set_xticks(x)
    axs[1, 1].set_xticklabels(dashpass_df['membership'])
    axs[1, 1].legend()
    axs[1, 1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add raw numbers as annotations
    for i, (_, row) in enumerate(dashpass_df.iterrows()):
        # Customer count annotation
        axs[1, 1].annotate(f"n={int(row['customer_count'])}", 
                          xy=(i - width/2, normalized_customer_count.iloc[i] + 5),
                          ha='center', fontsize=10)
        
        # Order count annotation
        axs[1, 1].annotate(f"n={int(row['order_count'])}", 
                          xy=(i + width/2, normalized_order_count.iloc[i] + 5),
                          ha='center', fontsize=10)
    
    # Add overall title
    fig.suptitle('Impact of DashPass Subscription', fontsize=20)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig('visualizations/dashpass_impact.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_driver_performance(driver_performance_df):
    """Plot driver performance metrics by vehicle type"""
    plt.figure(figsize=(14, 8))
    
    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
    
    # Sort by average delivery time
    driver_performance_df = driver_performance_df.sort_values('avg_delivery_time')
    
    # Plot 1: Average delivery time by vehicle type
    bars1 = ax1.barh(driver_performance_df['vehicle_type'], driver_performance_df['avg_delivery_time'], 
                    color='teal', alpha=0.7)
    ax1.set_xlabel('Average Delivery Time (minutes)')
    ax1.set_ylabel('Vehicle Type')
    ax1.set_title('Average Delivery Time by Vehicle Type')
    ax1.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add driver count and deliveries per driver as text labels
    for i, (_, row) in enumerate(driver_performance_df.iterrows()):
        ax1.text(row['avg_delivery_time'] + 1, i, 
                f"n={int(row['driver_count'])} ({row['deliveries_per_driver']:.1f} del/driver)", 
                va='center', fontsize=10)
    
    # Plot 2: Average rating and late percentage by vehicle type
    # Set x positions for bars
    x = np.arange(len(driver_performance_df))
    width = 0.35
    
    # Sort by average rating for the second plot
    driver_performance_df = driver_performance_df.sort_values('avg_rating', ascending=False)
    
    # Primary y-axis - average rating
    bars2 = ax2.bar(x - width/2, driver_performance_df['avg_rating'], 
                   width, color='green', alpha=0.7, label='Avg Rating')
    ax2.set_ylabel('Average Rating', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.set_ylim(3.5, 5.0)  # Set y-limits for better visualization of ratings
    
    # Secondary y-axis - late percentage
    ax3 = ax2.twinx()
    bars3 = ax3.bar(x + width/2, driver_performance_df['late_percentage'], 
                   width, color='red', alpha=0.7, label='Late %')
    ax3.set_ylabel('Late Percentage (%)', color='red')
    ax3.tick_params(axis='y', labelcolor='red')
    
    # Set x-axis ticks and labels
    ax2.set_xticks(x)
    ax2.set_xticklabels(driver_performance_df['vehicle_type'])
    ax2.set_title('Rating vs. Late Percentage by Vehicle Type')
    
    # Add a legend
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax2.legend(lines2 + lines3, labels2 + labels3, loc='upper right')
    
    # Add overall title
    fig.suptitle('Driver Performance by Vehicle Type', fontsize=20)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig('visualizations/driver_performance.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_popular_cuisines(popular_cuisines_df):
    """Plot most popular cuisines"""
    plt.figure(figsize=(14, 8))
    
    # Take top 15 cuisines for better readability
    top_cuisines = popular_cuisines_df.head(15)
    
    # Create a horizontal bar chart for order count
    bars = plt.barh(top_cuisines['cuisine'], top_cuisines['order_count'], 
                   color='royalblue', alpha=0.7)
    
    # Add restaurant count and average order value as text labels
    for i, (_, row) in enumerate(top_cuisines.iterrows()):
        # FIX: Escape dollar sign in text to prevent MathText parsing errors
        avg_order_value_text = f"${row['avg_order_value']:.2f}".replace('$', r'\$')
        plt.text(row['order_count'] + 5, i, 
                f"n={int(row['restaurant_count'])} restaurants ({avg_order_value_text} avg)", 
                va='center')
    
    # Customize plot
    plt.xlabel('Number of Orders')
    plt.ylabel('Cuisine')
    plt.title('Most Popular Cuisines by Order Count', fontsize=18)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('visualizations/popular_cuisines.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_weekly_trends(weekly_trends_df):
    """Plot weekly order trends"""
    plt.figure(figsize=(14, 8))
    
    # Define correct order of days for x-axis
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Sort the dataframe according to day order
    weekly_trends_df['day_index'] = weekly_trends_df['day_of_week'].map({day: i for i, day in enumerate(days_order)})
    weekly_trends_df = weekly_trends_df.sort_values('day_index')
    
    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Plot 1: Order count by day of week
    bars1 = ax1.bar(weekly_trends_df['day_of_week'], weekly_trends_df['order_count'], 
                   color='royalblue', alpha=0.7)
    ax1.set_ylabel('Number of Orders')
    ax1.set_title('Order Count by Day of Week')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add weekend highlight
    weekend_indices = [5, 6]  # Saturday and Sunday indices
    for idx in weekend_indices:
        if idx < len(ax1.get_children()):
            ax1.get_children()[idx].set_color('orange')
    
    # Add value labels on top of bars
    for i, v in enumerate(weekly_trends_df['order_count']):
        ax1.text(i, v + 10, str(int(v)), ha='center')
    
    # Plot 2: Average order value and total revenue by day of week
    ax2.plot(weekly_trends_df['day_of_week'], weekly_trends_df['avg_order_value'], 
            'go-', linewidth=2, markersize=8, label='Avg Order Value')
    ax2.set_ylabel('Average Order Value ($)', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels next to points
    for i, v in enumerate(weekly_trends_df['avg_order_value']):
        # FIX: Escape dollar sign to prevent MathText parsing errors
        value_text = f"${v:.2f}".replace('$', r'\$')
        ax2.text(i, v + 0.5, value_text, ha='center', color='green')
    
    # Add a second y-axis for total revenue
    ax3 = ax2.twinx()
    ax3.bar(weekly_trends_df['day_of_week'], weekly_trends_df['total_revenue'], 
           alpha=0.3, color='purple', label='Total Revenue')
    ax3.set_ylabel('Total Revenue ($)', color='purple')
    ax3.tick_params(axis='y', labelcolor='purple')
    
    # Add value labels inside bars
    for i, v in enumerate(weekly_trends_df['total_revenue']):
        # FIX: Escape dollar sign to prevent MathText parsing errors
        value_text = f"${int(v)}".replace('$', r'\$')
        # FIX: Use standard color name instead of "dark purple"
        ax3.text(i, v/2, value_text, ha='center', color='darkviolet')
    
    # Add a legend
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax2.legend(lines2 + lines3, labels2 + labels3, loc='upper left')
    
    # Set x-axis label
    plt.xlabel('Day of Week')
    
    # Add overall title
    fig.suptitle('Weekly Order Trends', fontsize=20)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig('visualizations/weekly_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_all_visualizations():
    """Create all visualizations"""
    # Create visualizations directory if it doesn't exist
    import os
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    
    # Set plotting style
    set_plotting_style()
    
    # Create analyzer
    analyzer = RestaurantAnalyzer()
    
    # Run all analyses
    results = analyzer.run_all_analyses()
    
    # Create visualizations
    plot_peak_order_hours(results['peak_hours'])
    plot_delivery_time_by_area(results['delivery_time_by_area'])
    plot_popular_restaurants(results['popular_restaurants'])
    plot_customer_retention(results['customer_retention'])
    plot_dashpass_impact(results['dashpass_impact'])
    plot_driver_performance(results['driver_performance'])
    plot_popular_cuisines(results['popular_cuisines'])
    plot_weekly_trends(results['weekly_trends'])
    
    # Close connection
    analyzer.close()
    
    print("All visualizations created successfully!")

if __name__ == "__main__":
    create_all_visualizations()