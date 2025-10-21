"""
Pandas profiling demonstration with complex multi-table joins.
Uses memory-profiler decorators and ydata-profiling for comprehensive analysis.
"""

import pandas as pd
import time
from pathlib import Path
from memory_profiler import profile
from ydata_profiling import ProfileReport

# Global variables to track execution times
timing_data = {}


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def load_datasets():
    """
    Load all three datasets using pandas.
    Compares CSV vs Parquet loading performance.
    """
    print_section("LOADING DATASETS WITH PANDAS")
    data_dir = Path('data')
    
    # Load from Parquet (faster and more efficient)
    start = time.time()
    df_orders = pd.read_parquet(data_dir / 'orders.parquet')
    df_customers = pd.read_parquet(data_dir / 'customers.parquet')
    df_products = pd.read_parquet(data_dir / 'products.parquet')
    load_time = time.time() - start
    
    timing_data['load_parquet'] = load_time
    
    print(f"✓ Loaded orders: {len(df_orders):,} rows")
    print(f"✓ Loaded customers: {len(df_customers):,} rows")
    print(f"✓ Loaded products: {len(df_products):,} rows")
    print(f"⏱  Loading time (Parquet): {load_time:.3f} seconds")
    
    # Show memory usage
    orders_mem = df_orders.memory_usage(deep=True).sum() / 1024**2
    customers_mem = df_customers.memory_usage(deep=True).sum() / 1024**2
    products_mem = df_products.memory_usage(deep=True).sum() / 1024**2
    total_mem = orders_mem + customers_mem + products_mem
    
    print(f"\n📊 Memory Usage:")
    print(f"   Orders: {orders_mem:.2f} MB")
    print(f"   Customers: {customers_mem:.2f} MB")
    print(f"   Products: {products_mem:.2f} MB")
    print(f"   Total: {total_mem:.2f} MB")
    
    return df_orders, df_customers, df_products


@profile
def perform_complex_joins(df_orders, df_customers, df_products):
    """
    Perform complex multi-table joins with pandas.
    Memory profiler decorator tracks memory usage line-by-line.
    
    Join Strategy:
    1. Left join orders with customers (keep all orders, even without customer data)
    2. Inner join result with products (only keep orders with valid products)
    3. Multiple join conditions and data enrichment
    """
    print_section("PERFORMING COMPLEX JOINS WITH PANDAS")
    
    # Step 1: Left join orders with customers
    print("\n📍 Step 1: Left joining orders with customers...")
    start = time.time()
    df_joined = df_orders.merge(
        df_customers,
        on='customer_id',
        how='left',
        suffixes=('_order', '_customer')
    )
    step1_time = time.time() - start
    timing_data['pandas_join_step1'] = step1_time
    print(f"   Result: {len(df_joined):,} rows")
    print(f"   Time: {step1_time:.3f} seconds")
    print(f"   Memory: {df_joined.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Step 2: Inner join with products
    print("\n📍 Step 2: Inner joining with products...")
    start = time.time()
    df_full = df_joined.merge(
        df_products,
        on='product_id',
        how='inner'
    )
    step2_time = time.time() - start
    timing_data['pandas_join_step2'] = step2_time
    print(f"   Result: {len(df_full):,} rows")
    print(f"   Time: {step2_time:.3f} seconds")
    print(f"   Memory: {df_full.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Data enrichment: Calculate total value per order
    print("\n📍 Step 3: Data enrichment...")
    start = time.time()
    # Use product price when amount is missing
    df_full['final_amount'] = df_full['amount'].fillna(df_full['price'])
    # Calculate revenue
    df_full['revenue'] = df_full['final_amount'] * (1.0 if 'quantity' not in df_full else df_full.get('quantity', 1))
    step3_time = time.time() - start
    timing_data['pandas_enrichment'] = step3_time
    print(f"   Time: {step3_time:.3f} seconds")
    
    total_join_time = step1_time + step2_time + step3_time
    timing_data['pandas_total_joins'] = total_join_time
    print(f"\n⏱  Total join time: {total_join_time:.3f} seconds")
    
    return df_full


@profile
def apply_filters_and_aggregations(df_full):
    """
    Apply complex filters and groupby aggregations.
    Memory profiler tracks memory usage for each operation.
    """
    print_section("APPLYING FILTERS AND AGGREGATIONS")
    
    # Filter 1: Only completed orders from 2023 onwards
    print("\n📍 Filter 1: Completed orders from 2023+...")
    start = time.time()
    df_filtered = df_full[
        (df_full['status'] == 'completed') & 
        (df_full['order_date'] >= '2023-01-01')
    ].copy()
    filter_time = time.time() - start
    timing_data['pandas_filter'] = filter_time
    print(f"   Result: {len(df_filtered):,} rows (from {len(df_full):,})")
    print(f"   Time: {filter_time:.3f} seconds")
    
    # Aggregation 1: Revenue by country and category
    print("\n📍 Aggregation 1: Revenue by country and category...")
    start = time.time()
    agg_country_category = df_filtered.groupby(['country', 'category']).agg({
        'revenue': ['sum', 'mean', 'count'],
        'final_amount': 'mean',
        'order_id': 'nunique'
    }).reset_index()
    agg1_time = time.time() - start
    timing_data['pandas_agg1'] = agg1_time
    print(f"   Result: {len(agg_country_category):,} groups")
    print(f"   Time: {agg1_time:.3f} seconds")
    
    # Aggregation 2: Customer segment analysis
    print("\n📍 Aggregation 2: Customer segment analysis...")
    start = time.time()
    agg_segment = df_filtered.groupby('segment').agg({
        'revenue': ['sum', 'mean', 'median', 'std'],
        'customer_id': 'nunique',
        'order_id': 'count'
    }).reset_index()
    agg2_time = time.time() - start
    timing_data['pandas_agg2'] = agg2_time
    print(f"   Result: {len(agg_segment):,} segments")
    print(f"   Time: {agg2_time:.3f} seconds")
    
    # Top customers by revenue
    print("\n📍 Aggregation 3: Top 100 customers by revenue...")
    start = time.time()
    top_customers = df_filtered.groupby(['customer_id', 'name', 'segment']).agg({
        'revenue': 'sum',
        'order_id': 'count'
    }).reset_index().sort_values('revenue', ascending=False).head(100)
    agg3_time = time.time() - start
    timing_data['pandas_agg3'] = agg3_time
    print(f"   Time: {agg3_time:.3f} seconds")
    
    total_agg_time = agg1_time + agg2_time + agg3_time
    timing_data['pandas_total_agg'] = total_agg_time
    print(f"\n⏱  Total aggregation time: {total_agg_time:.3f} seconds")
    
    return df_filtered, agg_country_category, agg_segment, top_customers


def generate_profiling_report(df_full, output_path='pandas_profile_report.html'):
    """
    Generate comprehensive HTML profiling report using ydata-profiling.
    This creates a detailed analysis of the dataset including:
    - Dataset overview and statistics
    - Variable distributions
    - Correlations
    - Missing values analysis
    - Sample data
    """
    print_section("GENERATING YDATA-PROFILING REPORT")
    print(f"Analyzing dataset with {len(df_full):,} rows and {len(df_full.columns)} columns...")
    print("This may take a few minutes for large datasets...")
    
    start = time.time()
    
    # Create profile with optimized settings for large datasets
    profile = ProfileReport(
        df_full,
        title="E-Commerce Joined Dataset Profile",
        minimal=False,  # Set to True for faster but less detailed report
        explorative=True,
        dark_mode=False
    )
    
    # Save report
    profile.to_file(output_path)
    report_time = time.time() - start
    timing_data['pandas_profiling_report'] = report_time
    
    print(f"✓ Report saved to: {output_path}")
    print(f"⏱  Report generation time: {report_time:.3f} seconds")


def print_summary():
    """Print execution summary with all timing information."""
    print_section("PANDAS PROFILING SUMMARY")
    
    print("\n📊 Execution Times:")
    print(f"   Data Loading:           {timing_data.get('load_parquet', 0):.3f}s")
    print(f"   Join Step 1:            {timing_data.get('pandas_join_step1', 0):.3f}s")
    print(f"   Join Step 2:            {timing_data.get('pandas_join_step2', 0):.3f}s")
    print(f"   Data Enrichment:        {timing_data.get('pandas_enrichment', 0):.3f}s")
    print(f"   Total Joins:            {timing_data.get('pandas_total_joins', 0):.3f}s")
    print(f"   Filtering:              {timing_data.get('pandas_filter', 0):.3f}s")
    print(f"   Aggregations:           {timing_data.get('pandas_total_agg', 0):.3f}s")
    print(f"   Profiling Report:       {timing_data.get('pandas_profiling_report', 0):.3f}s")
    
    total_time = sum(timing_data.values())
    print(f"\n⏱  TOTAL EXECUTION TIME:   {total_time:.3f}s")
    
    print("\n💡 Performance Tips:")
    print("   - Use Parquet format for faster loading")
    print("   - Consider data types optimization (category dtype for strings)")
    print("   - Use chunking for very large datasets")
    print("   - Profile memory usage to identify bottlenecks")


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print(" " * 15 + "PANDAS PROFILING DEMONSTRATION")
    print("=" * 70)
    
    overall_start = time.time()
    
    # Load datasets
    df_orders, df_customers, df_products = load_datasets()
    
    # Perform complex joins
    df_full = perform_complex_joins(df_orders, df_customers, df_products)
    
    # Apply filters and aggregations
    df_filtered, agg_country, agg_segment, top_customers = apply_filters_and_aggregations(df_full)
    
    # Show sample results
    print_section("SAMPLE RESULTS")
    print("\nTop 5 Customer Segments by Revenue:")
    print(agg_segment.head())
    
    print("\nTop 10 Customers:")
    print(top_customers.head(10))
    
    # Generate profiling report
    generate_profiling_report(df_full)
    
    # Print summary
    timing_data['overall'] = time.time() - overall_start
    print_summary()
    
    print("\n" + "=" * 70)
    print("✓ Pandas profiling demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
