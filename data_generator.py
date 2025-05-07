import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

# Configure the time period for our data
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

# Helper function to generate random datetime within our range
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    
    # Add random hour, minute, second
    hour = random.randint(6, 23)  # Most food delivery happens between 6 AM and 11 PM
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return random_date.replace(hour=hour, minute=minute, second=second)

# Helper function to create weighted random choices
def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]

# Generate Restaurant Data
def generate_restaurants(num_restaurants=50):  # Reduced from 200 to 50
    cuisines = ['Italian', 'Chinese', 'Mexican', 'Indian', 'American', 'Japanese', 
                'Thai', 'Mediterranean', 'Vietnamese', 'Korean', 'Greek', 'French', 
                'Spanish', 'Middle Eastern', 'Burger', 'Pizza', 'Sushi', 'BBQ', 
                'Vegetarian', 'Vegan', 'Seafood', 'Steakhouse']  # Reduced number of cuisines
    
    price_ranges = ['$', '$$', '$$$', '$$$$']
    price_weights = [0.3, 0.4, 0.2, 0.1]  # More common to have mid-range restaurants
    
    restaurants = []
    
    for i in range(num_restaurants):
        restaurant_id = str(uuid.uuid4())
        name = fake.company()
        cuisine = random.choice(cuisines)
        price_range = weighted_choice(price_ranges, price_weights)
        rating = round(random.uniform(2.5, 5.0), 1)  # Most restaurants have decent ratings
        
        # Generate addresses in different areas for geographical analysis
        area = random.choice(['Downtown', 'Uptown', 'Midtown', 'West Side', 'East Side'])  # Reduced number of areas
        address = f"{fake.building_number()} {fake.street_name()}, {area}"
        
        latitude = round(random.uniform(40.5, 41.0), 6)  # Simulated coordinates
        longitude = round(random.uniform(-74.0, -73.5), 6)
        
        # Is the restaurant part of DoorDash's subscription program?
        is_dashpass = random.random() < 0.7  # 70% of restaurants are in DashPass
        
        # Average preparation time in minutes
        prep_time = random.randint(10, 40)
        
        restaurants.append({
            'restaurant_id': restaurant_id,
            'name': name,
            'cuisine': cuisine,
            'price_range': price_range,
            'rating': rating,
            'address': address,
            'area': area,
            'latitude': latitude,
            'longitude': longitude,
            'is_dashpass': is_dashpass,
            'avg_prep_time_min': prep_time
        })
    
    return pd.DataFrame(restaurants)

# Generate Menu Items Data
def generate_menu_items(restaurants_df, avg_items_per_restaurant=10):  # Reduced from 15 to 10
    menu_items = []
    
    for _, restaurant in restaurants_df.iterrows():
        restaurant_id = restaurant['restaurant_id']
        cuisine = restaurant['cuisine']
        price_range = restaurant['price_range']
        
        # Number of menu items varies by restaurant
        num_items = max(5, int(np.random.normal(avg_items_per_restaurant, 3)))  # Reduced standard deviation
        
        # Price base depends on restaurant price range
        if price_range == '$':
            base_price = 8
            std_dev = 3
        elif price_range == '$$':
            base_price = 15
            std_dev = 5
        elif price_range == '$$$':
            base_price = 25
            std_dev = 8
        else:  # '$$$$'
            base_price = 40
            std_dev = 15
        
        for i in range(num_items):
            item_id = str(uuid.uuid4())
            
            # Generate a more realistic food name based on cuisine
            if cuisine == 'Italian':
                item_name = random.choice(['Pasta', 'Pizza', 'Risotto', 'Lasagna']) + ' ' + \
                           random.choice(['Bolognese', 'Carbonara', 'Margherita', 'Quattro Formaggi', 'al Pesto'])
            elif cuisine == 'Mexican':
                item_name = random.choice(['Taco', 'Burrito', 'Enchilada', 'Quesadilla', 'Nachos']) + ' ' + \
                           random.choice(['de Pollo', 'de Carne', 'Vegetariano', 'con Queso', 'Supremo'])
            else:
                item_name = fake.word().capitalize() + ' ' + random.choice(['Plate', 'Bowl', 'Special', 'Delight', 'Combo'])
            
            price = round(max(5, random.normalvariate(base_price, std_dev)), 2)
            
            # Is this item popular?
            is_popular = random.random() < 0.2  # 20% of items are marked as popular
            
            # Categories
            categories = ['Appetizer', 'Main Course', 'Side', 'Dessert', 'Beverage']
            category_weights = [0.2, 0.5, 0.15, 0.1, 0.05]  # Most items are main courses
            category = weighted_choice(categories, category_weights)
            
            menu_items.append({
                'item_id': item_id,
                'restaurant_id': restaurant_id,
                'name': item_name,
                'price': price,
                'category': category,
                'is_popular': is_popular
            })
    
    return pd.DataFrame(menu_items)

# Generate Customer Data
def generate_customers(num_customers=200):  # Reduced from 1000 to 200
    customers = []
    
    # Define customer segments
    segments = ['New', 'Occasional', 'Regular', 'Frequent', 'VIP']
    segment_weights = [0.15, 0.25, 0.3, 0.2, 0.1]  # Distribution of customer segments
    
    for i in range(num_customers):
        customer_id = str(uuid.uuid4())
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        
        # Generate addresses in different areas for geographical analysis
        area = random.choice(['Downtown', 'Uptown', 'Midtown', 'West Side', 'East Side'])  # Reduced number of areas
        address = f"{fake.building_number()} {fake.street_name()}, {area}"
        
        latitude = round(random.uniform(40.5, 41.0), 6)  # Simulated coordinates
        longitude = round(random.uniform(-74.0, -73.5), 6)
        
        # Registration date
        registration_date = random_date(start_date - timedelta(days=365*2), end_date)
        
        # Has DashPass subscription?
        has_dashpass = random.random() < 0.4  # 40% of customers have DashPass
        
        # Customer segment (New, Occasional, Regular, Frequent, VIP)
        segment = weighted_choice(segments, segment_weights)
        
        customers.append({
            'customer_id': customer_id,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'area': area,
            'latitude': latitude,
            'longitude': longitude,
            'registration_date': registration_date,
            'has_dashpass': has_dashpass,
            'segment': segment
        })
    
    return pd.DataFrame(customers)

# Generate Driver Data
def generate_drivers(num_drivers=100):  # Reduced from 500 to 100
    drivers = []
    
    vehicle_types = ['Car', 'Motorcycle', 'Bicycle', 'Scooter', 'On foot']
    vehicle_weights = [0.6, 0.2, 0.1, 0.08, 0.02]  # Most drivers use cars
    
    for i in range(num_drivers):
        driver_id = str(uuid.uuid4())
        name = fake.name()
        phone = fake.phone_number()
        
        # Vehicle type
        vehicle = weighted_choice(vehicle_types, vehicle_weights)
        
        # Rating
        rating = round(random.uniform(3.0, 5.0), 1)  # Drivers generally have good ratings
        
        # Start date
        start_date_driver = random_date(start_date - timedelta(days=365*3), end_date)
        
        # Calculate average deliveries per week (active drivers do more)
        avg_deliveries_per_week = random.randint(10, 50)
        
        # Driver status
        status_options = ['Active', 'Inactive', 'On leave', 'New']
        status_weights = [0.7, 0.15, 0.1, 0.05]
        status = weighted_choice(status_options, status_weights)
        
        drivers.append({
            'driver_id': driver_id,
            'name': name,
            'phone': phone,
            'vehicle_type': vehicle,
            'rating': rating,
            'start_date': start_date_driver,
            'avg_deliveries_per_week': avg_deliveries_per_week,
            'status': status
        })
    
    return pd.DataFrame(drivers)

# Generate Orders and Order Items
def generate_orders_and_items(customers_df, restaurants_df, menu_items_df, num_orders=2000):  # Reduced from 10000 to 2000
    orders = []
    order_items = []
    
    # Define days of week for seasonality
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Weekends are busier
    day_weights = [0.1, 0.1, 0.12, 0.13, 0.15, 0.2, 0.2]
    
    # Define meal times with weights (lunch and dinner are busier)
    meal_times = {
        'Breakfast': (6, 10),  # 6 AM - 10 AM
        'Lunch': (11, 14),     # 11 AM - 2 PM
        'Afternoon': (15, 16), # 3 PM - 4 PM
        'Dinner': (17, 21),    # 5 PM - 9 PM
        'Late Night': (22, 5)  # 10 PM - 5 AM
    }
    
    meal_weights = {
        'Breakfast': 0.15,
        'Lunch': 0.3,
        'Afternoon': 0.1,
        'Dinner': 0.35,
        'Late Night': 0.1
    }
    
    # Status options
    status_options = ['Completed', 'Cancelled', 'Refunded']
    status_weights = [0.93, 0.05, 0.02]  # Most orders are completed successfully
    
    # Payment methods
    payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Apple Pay', 'Google Pay', 'Cash']
    payment_weights = [0.4, 0.3, 0.15, 0.08, 0.05, 0.02]
    
    # Get list of customer IDs and restaurant IDs for easy sampling
    customer_ids = customers_df['customer_id'].tolist()
    restaurant_ids = restaurants_df['restaurant_id'].tolist()
    
    # Create a dictionary to lookup restaurant details faster
    restaurant_lookup = restaurants_df.set_index('restaurant_id').to_dict('index')
    
    # Create a dictionary to lookup menu items by restaurant
    menu_by_restaurant = menu_items_df.groupby('restaurant_id')['item_id'].apply(list).to_dict()
    menu_items_lookup = menu_items_df.set_index('item_id').to_dict('index')
    
    for i in range(num_orders):
        order_id = str(uuid.uuid4())
        
        # Select a customer with weighted probability (frequent customers order more)
        customer_weights = []
        for _, customer in customers_df.iterrows():
            if customer['segment'] == 'VIP':
                weight = 5.0
            elif customer['segment'] == 'Frequent':
                weight = 3.0
            elif customer['segment'] == 'Regular':
                weight = 2.0
            elif customer['segment'] == 'Occasional':
                weight = 1.0
            else:  # New
                weight = 0.5
            customer_weights.append(weight)
        
        customer_id = random.choices(customer_ids, weights=customer_weights, k=1)[0]
        customer_info = customers_df[customers_df['customer_id'] == customer_id].iloc[0]
        
        # Select day of week with weighted probability
        day_of_week = random.choices(days_of_week, weights=day_weights, k=1)[0]
        
        # Generate order date/time with meal time weighting
        order_date = random_date(start_date, end_date)
        
        # Adjust hour based on meal time preference
        meal_type = weighted_choice(list(meal_times.keys()), list(meal_weights.values()))
        start_hour, end_hour = meal_times[meal_type]
        
        if start_hour < end_hour:  # Normal time range
            hour = random.randint(start_hour, end_hour)
        else:  # Late night crossing midnight
            if random.random() < 0.6:  # 60% before midnight
                hour = random.randint(start_hour, 23)
            else:  # 40% after midnight
                hour = random.randint(0, end_hour)
        
        order_date = order_date.replace(hour=hour, minute=random.randint(0, 59))
        
        # Select a restaurant (with preference for local and higher rated)
        # We'll use a simple proximity simulation by comparing areas
        restaurant_selection_weights = []
        for r_id in restaurant_ids:
            r_info = restaurant_lookup[r_id]
            # Higher rated restaurants are selected more often
            rating_factor = r_info['rating'] / 5.0 * 2.0
            # Local restaurants are selected more often
            nearby_weight = 3.0 if r_info['area'] == customer_info['area'] else 1.0
            # DashPass restaurants are selected more often by DashPass customers
            dashpass_factor = 1.5 if (r_info['is_dashpass'] and customer_info['has_dashpass']) else 1.0
            
            weight = nearby_weight * rating_factor * dashpass_factor
            restaurant_selection_weights.append(weight)

        restaurant_id = random.choices(restaurant_ids, weights=restaurant_selection_weights, k=1)[0]
        restaurant_info = restaurant_lookup[restaurant_id]
        
        # Order status
        status = weighted_choice(status_options, status_weights)
        
        # Payment method
        payment_method = weighted_choice(payment_methods, payment_weights)
        
        # Calculate order details
        items_count = max(1, int(np.random.lognormal(1.1, 0.3)))  # Most orders have 2-4 items
        
        # Select menu items for this restaurant
        restaurant_menu = menu_by_restaurant.get(restaurant_id, [])
        if not restaurant_menu:
            continue  # Skip if no menu items for this restaurant
        
        # Sample menu items (with replacement to allow ordering multiple of same item)
        selected_items = random.choices(restaurant_menu, k=items_count)
        
        # Calculate subtotal
        subtotal = sum(menu_items_lookup[item_id]['price'] for item_id in selected_items)
        
        # Calculate taxes (assume 8% tax rate)
        tax = round(subtotal * 0.08, 2)
        
        # Delivery fee (based on restaurant's price range and DashPass status)
        if customer_info['has_dashpass'] and restaurant_info['is_dashpass']:
            delivery_fee = 0.0
        else:
            base_fee = {
                '$': 2.99,
                '$$': 3.99,
                '$$$': 4.99,
                '$$$$': 5.99
            }[restaurant_info['price_range']]
            
            # Add distance factor (simulated by area difference)
            distance_fee = 0.0 if restaurant_info['area'] == customer_info['area'] else 2.0
            delivery_fee = round(base_fee + distance_fee, 2)
        
        # Tip (most customers tip between 15-20%)
        tip_percentage = random.uniform(0.0, 0.25)  # 0-25% tip
        tip = round(subtotal * tip_percentage, 2)
        
        # Total
        total = subtotal + tax + delivery_fee + tip
        
        # Promo discount (occasional random promotions)
        promo_discount = 0.0
        if random.random() < 0.15:  # 15% of orders have a promotion
            promo_discount = round(min(10.0, subtotal * 0.2), 2)  # Max $10 or 20% off
        
        # Final total after discount
        final_total = max(0, total - promo_discount)
        
        orders.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'restaurant_id': restaurant_id,
            'order_date': order_date,
            'day_of_week': day_of_week,
            'meal_time': meal_type,
            'status': status,
            'items_count': items_count,
            'subtotal': subtotal,
            'tax': tax,
            'delivery_fee': delivery_fee,
            'tip': tip,
            'promo_discount': promo_discount,
            'total': final_total,
            'payment_method': payment_method
        })
        
        # Generate order items
        for item_id in selected_items:
            order_item_id = str(uuid.uuid4())
            item_price = menu_items_lookup[item_id]['price']
            
            # Sometimes people order multiple of the same item
            quantity = 1
            if random.random() < 0.2:  # 20% chance of ordering multiple
                quantity = random.randint(2, 4)
            
            # Special instructions
            has_instructions = random.random() < 0.3  # 30% chance of special instructions
            instructions = None
            if has_instructions:
                instructions = random.choice([
                    "No onions please",
                    "Extra spicy",
                    "Dressing on the side",
                    "No cilantro",
                    "Add extra sauce",
                    "Well done",
                    "Substitute fries for salad",
                    "Extra napkins please",
                    "No ice in the drink",
                    "Gluten-free if possible"
                ])
            
            order_items.append({
                'order_item_id': order_item_id,
                'order_id': order_id,
                'item_id': item_id,
                'quantity': quantity,
                'price': item_price,
                'special_instructions': instructions
            })
    
    return pd.DataFrame(orders), pd.DataFrame(order_items)

# Generate Delivery Data
def generate_deliveries(orders_df, drivers_df):
    deliveries = []
    
    # Filter for completed orders only
    completed_orders = orders_df[orders_df['status'] == 'Completed']
    
    # Get driver IDs for sampling
    driver_ids = drivers_df['driver_id'].tolist()
    driver_lookup = drivers_df.set_index('driver_id').to_dict('index')
    
    for _, order in completed_orders.iterrows():
        delivery_id = str(uuid.uuid4())
        order_id = order['order_id']
        
        # Assign a driver (weighted by their average deliveries per week)
        driver_weights = [driver_lookup[d_id]['avg_deliveries_per_week'] for d_id in driver_ids]
        driver_id = random.choices(driver_ids, weights=driver_weights, k=1)[0]
        
        # Order estimated delivery time (based on restaurant prep time)
        restaurant_id = order['restaurant_id']
        
        # Calculate estimated delivery time
        order_date = order['order_date']
        
        # Estimated delivery time factors:
        # 1. Restaurant prep time (from restaurant info)
        # 2. Time of day (rush hours take longer)
        # 3. Day of week (weekends can be busier)
        # 4. Weather conditions (random factor)
        
        # Base delivery time (in minutes)
        base_delivery_time = 30  # Average 30 minutes
        
        # Rush hour factor (weekdays 11:30-1:30 PM and 5:30-7:30 PM)
        is_lunch_rush = order_date.weekday() < 5 and 11.5 <= order_date.hour <= 13.5
        is_dinner_rush = 17.5 <= order_date.hour <= 19.5
        
        rush_factor = 1.0
        if is_lunch_rush or is_dinner_rush:
            rush_factor = 1.3
        
        # Weekend factor
        weekend_factor = 1.2 if order_date.weekday() >= 5 else 1.0
        
        # Weather factor (random simulation)
        weather_factor = random.uniform(0.9, 1.4)  # Bad weather can increase delivery time
        
        # Calculate estimated delivery time
        est_delivery_minutes = base_delivery_time * rush_factor * weekend_factor * weather_factor
        est_delivery_time = order_date + timedelta(minutes=int(est_delivery_minutes))
        
        # Actual delivery time (with some random variation)
        # Most deliveries are on time, some are early, some are late
        time_variation = random.normalvariate(0, 10)  # Standard deviation of 10 minutes
        actual_delivery_minutes = max(5, est_delivery_minutes + time_variation)
        actual_delivery_time = order_date + timedelta(minutes=int(actual_delivery_minutes))
        
        # Delivery status
        status = 'Delivered'
        
        # Customer rating (not all customers leave ratings)
        has_rating = random.random() < 0.7  # 70% of deliveries get rated
        delivery_rating = None
        if has_rating:
            # Most ratings are high, with occasional low ones
            rating_distribution = [1, 2, 3, 4, 5]
            rating_weights = [0.01, 0.04, 0.1, 0.25, 0.6]  # Heavy weight towards 5 stars
            delivery_rating = weighted_choice(rating_distribution, rating_weights)
        
        # Issues reported
        has_issue = random.random() < 0.1  # 10% of deliveries have issues
        issue = None
        if has_issue:
            issues = [
                'Food was cold',
                'Missing items',
                'Late delivery',
                'Wrong order',
                'Damaged packaging',
                'Incorrect address',
                'Driver was unprofessional',
                'Food quality issue'
            ]
            issue = random.choice(issues)
        
        deliveries.append({
            'delivery_id': delivery_id,
            'order_id': order_id,
            'driver_id': driver_id,
            'estimated_delivery_time': est_delivery_time,
            'actual_delivery_time': actual_delivery_time,
            'delivery_duration_minutes': actual_delivery_minutes,
            'status': status,
            'customer_rating': delivery_rating,
            'issue_reported': issue
        })
    
    return pd.DataFrame(deliveries)

# Generate all data
def generate_all_data():
    print("Generating restaurants data...")
    restaurants = generate_restaurants(50)  # Reduced from 200 to 50
    
    print("Generating menu items data...")
    menu_items = generate_menu_items(restaurants, 10)  # Reduced average from 15 to 10
    
    print("Generating customers data...")
    customers = generate_customers(200)  # Reduced from 1000 to 200
    
    print("Generating drivers data...")
    drivers = generate_drivers(100)  # Reduced from 500 to 100
    
    print("Generating orders and order items data...")
    orders, order_items = generate_orders_and_items(customers, restaurants, menu_items, 2000)  # Reduced from 10000 to 2000
    
    print("Generating deliveries data...")
    deliveries = generate_deliveries(orders, drivers)
    
    # Save data to CSV files
    restaurants.to_csv('data/restaurants.csv', index=False)
    menu_items.to_csv('data/menu_items.csv', index=False)
    customers.to_csv('data/customers.csv', index=False)
    drivers.to_csv('data/drivers.csv', index=False)
    orders.to_csv('data/orders.csv', index=False)
    order_items.to_csv('data/order_items.csv', index=False)
    deliveries.to_csv('data/deliveries.csv', index=False)
    
    print(f"Generated data summary:")
    print(f"- Restaurants: {len(restaurants)}")
    print(f"- Menu Items: {len(menu_items)}")
    print(f"- Customers: {len(customers)}")
    print(f"- Drivers: {len(drivers)}")
    print(f"- Orders: {len(orders)}")
    print(f"- Order Items: {len(order_items)}")
    print(f"- Deliveries: {len(deliveries)}")
    
    return {
        'restaurants': restaurants,
        'menu_items': menu_items,
        'customers': customers,
        'drivers': drivers,
        'orders': orders,
        'order_items': order_items,
        'deliveries': deliveries
    }

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Generate all data
    data = generate_all_data()
    print("Data generation complete!")