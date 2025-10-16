"""
Polars profiling demonstration with lazy execution and complex joins.
Showcases lazy vs eager execution and query optimization with .profile().
"""

import polars as pl
import time
from pathlib import Path

# Global variables to track execution times
timing_data = {}


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def load_datasets_lazy():
    """
    Load datasets using Polars LazyFrame for deferred execution.
    Lazy loading delays computation until explicitly triggered.
    """
    print_section("LOADING DATASETS WITH POLARS (LAZY MODE)")
    data_dir = Path('data')
    
    start = time.time()
    # LazyFrame - computation is deferred
    lf_orders = pl.scan_parquet(data_dir / 'orders.parquet')
    lf_customers = pl.scan_parquet(data_dir / 'customers.parquet')
    lf_products = pl.scan_parquet(data_dir / 'products.parquet')
    load_time = time.time() - start
    
    timing_data['load_lazy'] = load_time
    
    print(f"✓ Lazy frames created for orders, customers, and products")
    print(f"⏱  Lazy frame creation time: {load_time:.6f} seconds")
    print("\n💡 Note: Lazy frames don't load data immediately - computation is deferred!")
    
    return lf_orders, lf_customers, lf_products


def load_datasets_eager():
    """
    Load datasets using Polars DataFrame for immediate execution.
    Compare with lazy loading performance.
    """
    print_section("LOADING DATASETS WITH POLARS (EAGER MODE)")
    data_dir = Path('data')
    
    start = time.time()
    df_orders = pl.read_parquet(data_dir / 'orders.parquet')
    df_customers = pl.read_parquet(data_dir / 'customers.parquet')
    df_products = pl.read_parquet(data_dir / 'products.parquet')
    load_time = time.time() - start
    
    timing_data['load_eager'] = load_time
    
    print(f"✓ Loaded orders: {len(df_orders):,} rows")
    print(f"✓ Loaded customers: {len(df_customers):,} rows")
    print(f"✓ Loaded products: {len(df_products):,} rows")
    print(f"⏱  Eager loading time: {load_time:.3f} seconds")
    
    # Show memory usage (estimated)
    orders_mem = df_orders.estimated_size() / 1024**2
    customers_mem = df_customers.estimated_size() / 1024**2
    products_mem = df_products.estimated_size() / 1024**2
    total_mem = orders_mem + customers_mem + products_mem
    
    print(f"\n📊 Memory Usage (estimated):")
    print(f"   Orders: {orders_mem:.2f} MB")
    print(f"   Customers: {customers_mem:.2f} MB")
    print(f"   Products: {products_mem:.2f} MB")
    print(f"   Total: {total_mem:.2f} MB")
    
    return df_orders, df_customers, df_products


def perform_lazy_joins_with_profile(lf_orders, lf_customers, lf_products):
    """
    Perform complex joins using Polars lazy execution with .profile().
    The .profile() method shows query execution plan and timing breakdown.
    """
    print_section("PERFORMING LAZY JOINS WITH QUERY PROFILING")
    
    print("\n📍 Building lazy query plan...")
    print("   - Left join orders with customers")
    print("   - Inner join result with products")
    print("   - Enrich data with calculated fields")
    print("   - Apply filters")
    
    # Build the entire query as a lazy execution plan
    lazy_query = (
        lf_orders
        # Step 1: Left join with customers
        .join(lf_customers, on='customer_id', how='left')
        # Step 2: Inner join with products
        .join(lf_products, on='product_id', how='inner')
        # Step 3: Data enrichment
        .with_columns([
            # Use product price when amount is missing
            pl.when(pl.col('amount').is_null())
            .then(pl.col('price'))
            .otherwise(pl.col('amount'))
            .alias('final_amount')
        ])
        .with_columns([
            pl.col('final_amount').alias('revenue')
        ])
        # Step 4: Filter completed orders from 2023+
        .filter(
            (pl.col('status') == 'completed') &
            (pl.col('order_date') >= pl.date(2023, 1, 1))
        )
    )
    
    print("✓ Lazy query plan built (no execution yet)")
    
    # Execute with profiling
    print("\n📊 Executing query with profiling...")
    start = time.time()
    result_df, profile_info = lazy_query.profile()
    execution_time = time.time() - start
    
    timing_data['polars_lazy_with_profile'] = execution_time
    
    print(f"\n✓ Query executed: {len(result_df):,} rows")
    print(f"⏱  Total execution time: {execution_time:.3f} seconds")
    
    # Display profiling information
    print("\n" + "=" * 70)
    print("POLARS QUERY EXECUTION PROFILE")
    print("=" * 70)
    print(profile_info)
    
    return result_df, profile_info


def perform_eager_joins(df_orders, df_customers, df_products):
    """
    Perform the same joins using eager execution for comparison.
    Shows timing breakdown for each step.
    """
    print_section("PERFORMING EAGER JOINS (FOR COMPARISON)")
    
    # Step 1: Left join orders with customers
    print("\n📍 Step 1: Left joining orders with customers...")
    start = time.time()
    df_joined = df_orders.join(df_customers, on='customer_id', how='left')
    step1_time = time.time() - start
    timing_data['polars_eager_step1'] = step1_time
    print(f"   Result: {len(df_joined):,} rows")
    print(f"   Time: {step1_time:.3f} seconds")
    
    # Step 2: Inner join with products
    print("\n📍 Step 2: Inner joining with products...")
    start = time.time()
    df_full = df_joined.join(df_products, on='product_id', how='inner')
    step2_time = time.time() - start
    timing_data['polars_eager_step2'] = step2_time
    print(f"   Result: {len(df_full):,} rows")
    print(f"   Time: {step2_time:.3f} seconds")
    
    # Step 3: Data enrichment
    print("\n📍 Step 3: Data enrichment...")
    start = time.time()
    df_full = df_full.with_columns([
        pl.when(pl.col('amount').is_null())
        .then(pl.col('price'))
        .otherwise(pl.col('amount'))
        .alias('final_amount')
    ]).with_columns([
        pl.col('final_amount').alias('revenue')
    ])
    step3_time = time.time() - start
    timing_data['polars_eager_step3'] = step3_time
    print(f"   Time: {step3_time:.3f} seconds")
    
    # Step 4: Filter
    print("\n📍 Step 4: Filtering completed orders from 2023+...")
    start = time.time()
    df_filtered = df_full.filter(
        (pl.col('status') == 'completed') &
        (pl.col('order_date') >= pl.date(2023, 1, 1))
    )
    step4_time = time.time() - start
    timing_data['polars_eager_step4'] = step4_time
    print(f"   Result: {len(df_filtered):,} rows")
    print(f"   Time: {step4_time:.3f} seconds")
    
    total_time = step1_time + step2_time + step3_time + step4_time
    timing_data['polars_eager_total'] = total_time
    print(f"\n⏱  Total eager execution time: {total_time:.3f} seconds")
    
    return df_filtered


def perform_aggregations(df_filtered):
    """
    Perform complex aggregations with Polars.
    Shows efficient groupby operations with multiple aggregation functions.
    """
    print_section("PERFORMING AGGREGATIONS WITH POLARS")
    
    # Aggregation 1: Revenue by country and category
    print("\n📍 Aggregation 1: Revenue by country and category...")
    start = time.time()
    agg_country_category = df_filtered.group_by(['country', 'category']).agg([
        pl.col('revenue').sum().alias('total_revenue'),
        pl.col('revenue').mean().alias('avg_revenue'),
        pl.col('revenue').count().alias('order_count'),
        pl.col('final_amount').mean().alias('avg_amount'),
        pl.col('order_id').n_unique().alias('unique_orders')
    ])
    agg1_time = time.time() - start
    timing_data['polars_agg1'] = agg1_time
    print(f"   Result: {len(agg_country_category):,} groups")
    print(f"   Time: {agg1_time:.3f} seconds")
    
    # Aggregation 2: Customer segment analysis
    print("\n📍 Aggregation 2: Customer segment analysis...")
    start = time.time()
    agg_segment = df_filtered.group_by('segment').agg([
        pl.col('revenue').sum().alias('total_revenue'),
        pl.col('revenue').mean().alias('avg_revenue'),
        pl.col('revenue').median().alias('median_revenue'),
        pl.col('revenue').std().alias('std_revenue'),
        pl.col('customer_id').n_unique().alias('unique_customers'),
        pl.col('order_id').count().alias('order_count')
    ])
    agg2_time = time.time() - start
    timing_data['polars_agg2'] = agg2_time
    print(f"   Result: {len(agg_segment):,} segments")
    print(f"   Time: {agg2_time:.3f} seconds")
    
    # Top customers by revenue
    print("\n📍 Aggregation 3: Top 100 customers by revenue...")
    start = time.time()
    top_customers = (
        df_filtered
        .group_by(['customer_id', 'name', 'segment'])
        .agg([
            pl.col('revenue').sum().alias('total_revenue'),
            pl.col('order_id').count().alias('order_count')
        ])
        .sort('total_revenue', descending=True)
        .head(100)
    )
    agg3_time = time.time() - start
    timing_data['polars_agg3'] = agg3_time
    print(f"   Time: {agg3_time:.3f} seconds")
    
    total_agg_time = agg1_time + agg2_time + agg3_time
    timing_data['polars_total_agg'] = total_agg_time
    print(f"\n⏱  Total aggregation time: {total_agg_time:.3f} seconds")
    
    return agg_country_category, agg_segment, top_customers


def demonstrate_streaming():
    """
    Demonstrate Polars streaming capabilities for large datasets.
    Streaming allows processing data larger than RAM.
    """
    print_section("DEMONSTRATING STREAMING EXECUTION")
    
    data_dir = Path('data')
    
    print("\n📍 Building streaming query...")
    print("   Streaming allows processing datasets larger than available RAM")
    print("   by processing data in chunks.")
    
    start = time.time()
    
    # Build streaming query
    result = (
        pl.scan_parquet(data_dir / 'orders.parquet')
        .join(
            pl.scan_parquet(data_dir / 'customers.parquet'),
            on='customer_id',
            how='left'
        )
        .join(
            pl.scan_parquet(data_dir / 'products.parquet'),
            on='product_id',
            how='inner'
        )
        .group_by('country')
        .agg([
            pl.col('amount').sum().alias('total_amount'),
            pl.col('order_id').count().alias('order_count')
        ])
        .collect(streaming=True)  # Enable streaming execution
    )
    
    streaming_time = time.time() - start
    timing_data['polars_streaming'] = streaming_time
    
    print(f"\n✓ Streaming query executed: {len(result):,} rows")
    print(f"⏱  Streaming execution time: {streaming_time:.3f} seconds")
    print("\n💡 Streaming is most beneficial for datasets larger than RAM")
    
    return result


def print_summary():
    """Print detailed timing summary comparing lazy vs eager execution."""
    print_section("POLARS PROFILING SUMMARY")
    
    print("\n📊 Execution Times:")
    print(f"   Lazy Frame Creation:    {timing_data.get('load_lazy', 0):.6f}s")
    print(f"   Eager Loading:          {timing_data.get('load_eager', 0):.3f}s")
    print()
    print(f"   Lazy Join (profiled):   {timing_data.get('polars_lazy_with_profile', 0):.3f}s")
    print(f"   Eager Join Total:       {timing_data.get('polars_eager_total', 0):.3f}s")
    print(f"     - Step 1 (orders+cust): {timing_data.get('polars_eager_step1', 0):.3f}s")
    print(f"     - Step 2 (+products):   {timing_data.get('polars_eager_step2', 0):.3f}s")
    print(f"     - Step 3 (enrichment):  {timing_data.get('polars_eager_step3', 0):.3f}s")
    print(f"     - Step 4 (filter):      {timing_data.get('polars_eager_step4', 0):.3f}s")
    print()
    print(f"   Aggregations:           {timing_data.get('polars_total_agg', 0):.3f}s")
    print(f"   Streaming Query:        {timing_data.get('polars_streaming', 0):.3f}s")
    
    # Calculate speedup
    lazy_time = timing_data.get('polars_lazy_with_profile', 0)
    eager_time = timing_data.get('polars_eager_total', 0)
    if eager_time > 0:
        speedup = eager_time / lazy_time if lazy_time > 0 else 0
        print(f"\n⚡ Lazy vs Eager Speedup: {speedup:.2f}x")
    
    print("\n💡 Key Insights:")
    print("   - Lazy execution builds an optimized query plan before execution")
    print("   - Query optimizer can push filters down and eliminate redundant operations")
    print("   - Parallel execution is automatic with Polars")
    print("   - Use .profile() to understand query execution bottlenecks")
    print("   - Streaming enables processing datasets larger than RAM")


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print(" " * 15 + "POLARS PROFILING DEMONSTRATION")
    print("=" * 70)
    
    overall_start = time.time()
    
    # Load datasets (both lazy and eager for comparison)
    lf_orders, lf_customers, lf_products = load_datasets_lazy()
    df_orders, df_customers, df_products = load_datasets_eager()
    
    # Perform lazy joins with profiling
    result_lazy, profile_info = perform_lazy_joins_with_profile(lf_orders, lf_customers, lf_products)
    
    # Perform eager joins for comparison
    result_eager = perform_eager_joins(df_orders, df_customers, df_products)
    
    # Perform aggregations
    agg_country, agg_segment, top_customers = perform_aggregations(result_eager)
    
    # Show sample results
    print_section("SAMPLE RESULTS")
    print("\nTop Customer Segments by Revenue:")
    print(agg_segment.sort('total_revenue', descending=True))
    
    print("\nTop 10 Customers:")
    print(top_customers.head(10))
    
    # Demonstrate streaming
    streaming_result = demonstrate_streaming()
    print("\nRevenue by Country (Streaming Query):")
    print(streaming_result.sort('total_amount', descending=True).head(10))
    
    # Print summary
    timing_data['overall'] = time.time() - overall_start
    print_summary()
    
    print("\n" + "=" * 70)
    print("✓ Polars profiling demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
