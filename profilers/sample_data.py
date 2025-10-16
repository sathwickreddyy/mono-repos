"""
Generate sample datasets for pandas and polars profiling demonstration.
Creates realistic e-commerce data with orders, customers, and products tables.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_orders(n_orders=300_000, n_customers=50_000, n_products=10_000):
    """
    Generate orders dataset with 300K rows.
    Includes realistic date ranges, missing values, and various order statuses.
    """
    print(f"Generating {n_orders:,} orders...")
    
    # Generate date range from 2020 to 2025
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 10, 15)
    date_range = (end_date - start_date).days
    
    orders = {
        'order_id': [f'ORD{str(i).zfill(8)}' for i in range(1, n_orders + 1)],
        'customer_id': np.random.randint(1, n_customers + 1, n_orders),
        'product_id': np.random.randint(1, n_products + 1, n_orders),
        'order_date': [start_date + timedelta(days=random.randint(0, date_range)) 
                      for _ in range(n_orders)],
        'amount': np.round(np.random.lognormal(4.5, 1.2, n_orders), 2),  # Realistic price distribution
        'status': np.random.choice(
            ['completed', 'pending', 'cancelled', 'shipped', 'returned'],
            n_orders,
            p=[0.70, 0.10, 0.08, 0.10, 0.02]
        )
    }
    
    df_orders = pd.DataFrame(orders)
    
    # Introduce ~5% missing values in amount column
    missing_indices = np.random.choice(df_orders.index, size=int(n_orders * 0.05), replace=False)
    df_orders.loc[missing_indices, 'amount'] = np.nan
    
    return df_orders


def generate_customers(n_customers=50_000):
    """
    Generate customers dataset with 50K rows.
    Includes names, countries, segments, and registration dates.
    """
    print(f"Generating {n_customers:,} customers...")
    
    countries = ['USA', 'UK', 'Germany', 'France', 'Canada', 'Australia', 'Japan', 'India', 'Brazil', 'Mexico']
    segments = ['Premium', 'Standard', 'Basic', 'VIP']
    
    first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 
                   'James', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Thomas']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                  'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Taylor', 'Thomas']
    
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2025, 10, 15)
    date_range = (end_date - start_date).days
    
    customers = {
        'customer_id': range(1, n_customers + 1),
        'name': [f"{random.choice(first_names)} {random.choice(last_names)}" 
                for _ in range(n_customers)],
        'country': np.random.choice(countries, n_customers, p=[0.35, 0.15, 0.12, 0.10, 0.08, 
                                                                0.06, 0.05, 0.04, 0.03, 0.02]),
        'segment': np.random.choice(segments, n_customers, p=[0.15, 0.50, 0.30, 0.05]),
        'registration_date': [start_date + timedelta(days=random.randint(0, date_range)) 
                             for _ in range(n_customers)]
    }
    
    df_customers = pd.DataFrame(customers)
    
    # Introduce ~5% missing values in country column
    missing_indices = np.random.choice(df_customers.index, size=int(n_customers * 0.05), replace=False)
    df_customers.loc[missing_indices, 'country'] = np.nan
    
    return df_customers


def generate_products(n_products=10_000):
    """
    Generate products dataset with 10K rows.
    Includes categories, subcategories, prices, and stock levels.
    """
    print(f"Generating {n_products:,} products...")
    
    categories = {
        'Electronics': ['Laptops', 'Phones', 'Tablets', 'Accessories'],
        'Clothing': ['Men', 'Women', 'Kids', 'Shoes'],
        'Home': ['Furniture', 'Kitchen', 'Decor', 'Bedding'],
        'Sports': ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports'],
        'Books': ['Fiction', 'Non-Fiction', 'Academic', 'Children']
    }
    
    all_categories = []
    all_subcategories = []
    for cat, subcats in categories.items():
        for _ in range(n_products // len(categories)):
            all_categories.append(cat)
            all_subcategories.append(random.choice(subcats))
    
    # Fill remaining to reach n_products
    while len(all_categories) < n_products:
        cat = random.choice(list(categories.keys()))
        all_categories.append(cat)
        all_subcategories.append(random.choice(categories[cat]))
    
    products = {
        'product_id': range(1, n_products + 1),
        'category': all_categories[:n_products],
        'subcategory': all_subcategories[:n_products],
        'price': np.round(np.random.lognormal(4.0, 1.0, n_products), 2),
        'stock_level': np.random.randint(0, 1000, n_products)
    }
    
    df_products = pd.DataFrame(products)
    
    # Introduce ~5% missing values in price column
    missing_indices = np.random.choice(df_products.index, size=int(n_products * 0.05), replace=False)
    df_products.loc[missing_indices, 'price'] = np.nan
    
    return df_products


def main():
    """Generate all datasets and save in CSV and Parquet formats."""
    print("=" * 60)
    print("Generating Sample E-Commerce Datasets")
    print("=" * 60)
    
    # Create data directory if it doesn't exist
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Generate datasets
    df_orders = generate_orders()
    df_customers = generate_customers()
    df_products = generate_products()
    
    print("\n" + "=" * 60)
    print("Saving datasets...")
    print("=" * 60)
    
    # Save as CSV
    print("Saving CSV files...")
    df_orders.to_csv(data_dir / 'orders.csv', index=False)
    df_customers.to_csv(data_dir / 'customers.csv', index=False)
    df_products.to_csv(data_dir / 'products.csv', index=False)
    
    # Save as Parquet (more efficient for large datasets)
    print("Saving Parquet files...")
    df_orders.to_parquet(data_dir / 'orders.parquet', index=False)
    df_customers.to_parquet(data_dir / 'customers.parquet', index=False)
    df_products.to_parquet(data_dir / 'products.parquet', index=False)
    
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"Orders: {len(df_orders):,} rows, {df_orders.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Customers: {len(df_customers):,} rows, {df_customers.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Products: {len(df_products):,} rows, {df_products.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\n" + "=" * 60)
    print("Sample Data Preview")
    print("=" * 60)
    print("\nOrders (first 5 rows):")
    print(df_orders.head())
    print(f"\nMissing values in orders: {df_orders.isnull().sum().sum()}")
    
    print("\nCustomers (first 5 rows):")
    print(df_customers.head())
    print(f"\nMissing values in customers: {df_customers.isnull().sum().sum()}")
    
    print("\nProducts (first 5 rows):")
    print(df_products.head())
    print(f"\nMissing values in products: {df_products.isnull().sum().sum()}")
    
    print("\n" + "=" * 60)
    print("✓ Data generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
