import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine

def extract_data():
    """Extract data from CSV files"""
    data = {}
    csv_files = [
        'restaurants', 'menu_items', 'customers', 'drivers',
        'orders', 'order_items', 'deliveries'
    ]
    
    for file in csv_files:
        try:
            data[file] = pd.read_csv(f'data/{file}.csv')
            print(f"Loaded {file}.csv with {len(data[file])} rows")
        except Exception as e:
            print(f"Error loading {file}.csv: {e}")
    
    return data

def transform_data(data):
    """Clean and transform the data"""
    # Make a copy of the data to avoid modifying the original
    transformed = {k: v.copy() for k, v in data.items()}
    
    # 1. Handle missing values
    for table_name, df in transformed.items():
        for col in df.columns:
            # Fill numeric missing values with 0 or mean depending on the column
            if df[col].dtype in [np.float64, np.int64]:
                if 'price' in col or 'fee' in col or 'total' in col:
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df[col].mean())
            
            # Fill categorical missing values with 'Unknown'
            elif df[col].dtype == 'object':
                if col not in ['special_instructions', 'issue_reported']:  # These can be legitimately null
                    df[col] = df[col].fillna('Unknown')
    
    # 2. Format date columns
    date_cols = {
        'customers': ['registration_date'],
        'drivers': ['start_date'],
        'orders': ['order_date'],
        'deliveries': ['estimated_delivery_time', 'actual_delivery_time']
    }
    
    for table, cols in date_cols.items():
        if table in transformed:
            for col in cols:
                if col in transformed[table].columns:
                    transformed[table][col] = pd.to_datetime(transformed[table][col])
    
    # 3. Create derived features for orders
    if 'orders' in transformed:
        # Extract datetime components
        transformed['orders']['order_year'] = transformed['orders']['order_date'].dt.year
        transformed['orders']['order_month'] = transformed['orders']['order_date'].dt.month
        transformed['orders']['order_day'] = transformed['orders']['order_date'].dt.day
        transformed['orders']['order_hour'] = transformed['orders']['order_date'].dt.hour
        transformed['orders']['order_minute'] = transformed['orders']['order_date'].dt.minute
        
        # Weekend flag
        transformed['orders']['is_weekend'] = transformed['orders']['order_date'].dt.dayofweek >= 5
    
    # 4. Enhance deliveries data with delivery performance metrics
    if 'deliveries' in transformed:
        # Calculate delivery delay (positive means late, negative means early)
        if 'estimated_delivery_time' in transformed['deliveries'] and 'actual_delivery_time' in transformed['deliveries']:
            transformed['deliveries']['delivery_delay_minutes'] = (
                (transformed['deliveries']['actual_delivery_time'] - 
                 transformed['deliveries']['estimated_delivery_time']).dt.total_seconds() / 60
            )
            
            # Flag for late deliveries (more than 5 minutes late)
            transformed['deliveries']['is_late'] = transformed['deliveries']['delivery_delay_minutes'] > 5
    
    # 5. Calculate restaurant performance metrics
    if 'orders' in transformed and 'restaurants' in transformed:
        # Average order value by restaurant
        restaurant_metrics = (
            transformed['orders']
            .groupby('restaurant_id')
            .agg({
                'total': ['mean', 'count'],
                'tip': ['mean', 'sum']
            })
        )
        restaurant_metrics.columns = ['avg_order_value', 'order_count', 'avg_tip', 'total_tips']
        
        # Add these metrics back to the restaurants dataframe
        transformed['restaurants'] = pd.merge(
            transformed['restaurants'], 
            restaurant_metrics, 
            on='restaurant_id', 
            how='left'
        )
        
        # Fill NA values with 0 for restaurants with no orders
        for col in ['avg_order_value', 'order_count', 'avg_tip', 'total_tips']:
            if col in transformed['restaurants'].columns:
                transformed['restaurants'][col] = transformed['restaurants'][col].fillna(0)
    
    # 6. Enrich customer data with order history
    if 'orders' in transformed and 'customers' in transformed:
        # Calculate order metrics by customer
        customer_metrics = (
            transformed['orders']
            .groupby('customer_id')
            .agg({
                'order_id': 'count',
                'total': ['sum', 'mean'],
                'order_date': ['min', 'max']
            })
        )
        customer_metrics.columns = [
            'order_count', 'total_spent', 'avg_order_value', 
            'first_order_date', 'last_order_date'
        ]
        
        # Calculate days since last order
        customer_metrics['days_since_last_order'] = (
            datetime(2024, 1, 1) - customer_metrics['last_order_date']
        ).dt.days
        
        # Calculate customer lifetime in days
        customer_metrics['customer_lifetime_days'] = (
            customer_metrics['last_order_date'] - customer_metrics['first_order_date']
        ).dt.days
        
        # Add these metrics back to the customers dataframe
        transformed['customers'] = pd.merge(
            transformed['customers'], 
            customer_metrics, 
            on='customer_id', 
            how='left'
        )
        
        # Fill NA values with 0 for customers with no orders
        for col in ['order_count', 'total_spent', 'avg_order_value']:
            if col in transformed['customers'].columns:
                transformed['customers'][col] = transformed['customers'][col].fillna(0)
    
    return transformed

def load_data(data, connection_string):
    """Load transformed data into a database"""
    try:
        # Create database engine
        engine = create_engine(connection_string)
        
        # Load each dataframe into database
        for table_name, df in data.items():
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Loaded {len(df)} rows into {table_name} table")
        
        print("Data loading complete!")
        return True
    except Exception as e:
        print(f"Error loading data to database: {e}")
        return False

def run_etl_pipeline(connection_string):
    """Run the complete ETL pipeline"""
    print("Starting ETL pipeline...")
    
    # Extract data from CSV files
    print("Extracting data...")
    data = extract_data()
    
    # Transform the data
    print("Transforming data...")
    transformed_data = transform_data(data)
    
    # Load data into the database
    print("Loading data into database...")
    success = load_data(transformed_data, connection_string)
    
    if success:
        print("ETL pipeline completed successfully!")
    else:
        print("ETL pipeline failed.")
    
    return transformed_data

if __name__ == "__main__":
    # Define database connection string (SQLite for simplicity)
    # For PostgreSQL, use: postgresql://username:password@localhost:5432/Restaurant_analytics
    connection_string = "sqlite:///Restaurant_analytics.db"
    
    # Run the ETL pipeline
    transformed_data = run_etl_pipeline(connection_string)