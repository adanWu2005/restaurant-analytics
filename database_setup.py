import sqlite3
import os

def create_sqlite_database():
    """Create SQLite database with the required schema"""
    # Remove existing database file if it exists
    if os.path.exists('Restaurant_analytics.db'):
        os.remove('Restaurant_analytics.db')
    
    # Connect to the new database
    conn = sqlite3.connect('Restaurant_analytics.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE restaurants (
        restaurant_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        cuisine TEXT,
        price_range TEXT,
        rating REAL,
        address TEXT,
        area TEXT,
        latitude REAL,
        longitude REAL,
        is_dashpass INTEGER,
        avg_prep_time_min INTEGER,
        avg_order_value REAL,
        order_count INTEGER,
        avg_tip REAL,
        total_tips REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE menu_items (
        item_id TEXT PRIMARY KEY,
        restaurant_id TEXT,
        name TEXT NOT NULL,
        price REAL,
        category TEXT,
        is_popular INTEGER,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        area TEXT,
        latitude REAL,
        longitude REAL,
        registration_date TIMESTAMP,
        has_dashpass INTEGER,
        segment TEXT,
        order_count INTEGER,
        total_spent REAL,
        avg_order_value REAL,
        first_order_date TIMESTAMP,
        last_order_date TIMESTAMP,
        days_since_last_order INTEGER,
        customer_lifetime_days INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE drivers (
        driver_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT,
        vehicle_type TEXT,
        rating REAL,
        start_date TIMESTAMP,
        avg_deliveries_per_week INTEGER,
        status TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        restaurant_id TEXT,
        order_date TIMESTAMP,
        day_of_week TEXT,
        meal_time TEXT,
        status TEXT,
        items_count INTEGER,
        subtotal REAL,
        tax REAL,
        delivery_fee REAL,
        tip REAL,
        promo_discount REAL,
        total REAL,
        payment_method TEXT,
        order_year INTEGER,
        order_month INTEGER,
        order_day INTEGER,
        order_hour INTEGER,
        order_minute INTEGER,
        is_weekend INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE order_items (
        order_item_id TEXT PRIMARY KEY,
        order_id TEXT,
        item_id TEXT,
        quantity INTEGER,
        price REAL,
        special_instructions TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (item_id) REFERENCES menu_items (item_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE deliveries (
        delivery_id TEXT PRIMARY KEY,
        order_id TEXT,
        driver_id TEXT,
        estimated_delivery_time TIMESTAMP,
        actual_delivery_time TIMESTAMP,
        delivery_duration_minutes REAL,
        status TEXT,
        customer_rating INTEGER,
        issue_reported TEXT,
        delivery_delay_minutes REAL,
        is_late INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (driver_id) REFERENCES drivers (driver_id)
    )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX idx_orders_customer_id ON orders (customer_id)')
    cursor.execute('CREATE INDEX idx_orders_restaurant_id ON orders (restaurant_id)')
    cursor.execute('CREATE INDEX idx_orders_order_date ON orders (order_date)')
    cursor.execute('CREATE INDEX idx_order_items_order_id ON order_items (order_id)')
    cursor.execute('CREATE INDEX idx_deliveries_order_id ON deliveries (order_id)')
    cursor.execute('CREATE INDEX idx_deliveries_driver_id ON deliveries (driver_id)')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("SQLite database created successfully!")

def create_postgres_database(connection_params):
    """
    Create PostgreSQL database with the required schema
    
    Args:
        connection_params: dict with keys dbname, user, password, host, port
    """
    try:
        import psycopg2
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**connection_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'Restaurant_analytics'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE Restaurant_analytics")
        
        # Close connection and reconnect to the new database
        conn.close()
        
        connection_params['dbname'] = 'Restaurant_analytics'
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            cuisine TEXT,
            price_range TEXT,
            rating REAL,
            address TEXT,
            area TEXT,
            latitude REAL,
            longitude REAL,
            is_dashpass BOOLEAN,
            avg_prep_time_min INTEGER,
            avg_order_value REAL,
            order_count INTEGER,
            avg_tip REAL,
            total_tips REAL
        )
        ''')
        
        # Similar CREATE TABLE statements for other tables...
        # (Omitted for brevity - would be the same as SQLite but with BOOLEAN instead of INTEGER for boolean fields)
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders (restaurant_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders (order_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items (order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deliveries_order_id ON deliveries (order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deliveries_driver_id ON deliveries (driver_id)')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("PostgreSQL database created successfully!")
        
    except ImportError:
        print("psycopg2 package not installed. Install with: pip install psycopg2-binary")
    except Exception as e:
        print(f"Error creating PostgreSQL database: {e}")

if __name__ == "__main__":
    # Create SQLite database (default)
    create_sqlite_database()
    
    # Uncomment to create PostgreSQL database instead
    # postgres_conn_params = {
    #     'dbname': 'postgres',  # Initial connection to postgres database
    #     'user': 'your_username',
    #     'password': 'your_password',
    #     'host': 'localhost',
    #     'port': '5432'
    # }
    # create_postgres_database(postgres_conn_params)