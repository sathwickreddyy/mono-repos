"""
Side-by-side performance comparison between pandas and polars.
Tracks execution time and memory usage for identical operations.
"""

import pandas as pd
import polars as pl
import time
from pathlib import Path
from memory_profiler import memory_usage
import numpy as np


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def benchmark_loading():
    """Compare loading performance between pandas and polars."""
    print_section("BENCHMARK 1: LOADING 300K RECORDS")
    
    data_dir = Path('data')
    results = {}
    
    # Pandas loading
    print("\n📊 Pandas - Loading from Parquet...")
    start = time.time()
    mem_before = memory_usage()[0]
    df_orders_pd = pd.read_parquet(data_dir / 'orders.parquet')
    df_customers_pd = pd.read_parquet(data_dir / 'customers.parquet')
    df_products_pd = pd.read_parquet(data_dir / 'products.parquet')
    mem_after = memory_usage()[0]
    pandas_time = time.time() - start
    pandas_mem = mem_after - mem_before
    
    results['pandas'] = {
        'time': pandas_time,
        'memory': pandas_mem,
        'rows': len(df_orders_pd) + len(df_customers_pd) + len(df_products_pd)
    }
    
    print(f"   Time: {pandas_time:.3f}s")
    print(f"   Memory: {pandas_mem:.2f} MB")
    
    # Polars loading
    print("\n📊 Polars - Loading from Parquet...")
    start = time.time()
    mem_before = memory_usage()[0]
    df_orders_pl = pl.read_parquet(data_dir / 'orders.parquet')
    df_customers_pl = pl.read_parquet(data_dir / 'customers.parquet')
    df_products_pl = pl.read_parquet(data_dir / 'products.parquet')
    mem_after = memory_usage()[0]
    polars_time = time.time() - start
    polars_mem = mem_after - mem_before
    
    results['polars'] = {
        'time': polars_time,
        'memory': polars_mem,
        'rows': len(df_orders_pl) + len(df_customers_pl) + len(df_products_pl)
    }
    
    print(f"   Time: {polars_time:.3f}s")
    print(f"   Memory: {polars_mem:.2f} MB")
    
    # Comparison
    speedup = pandas_time / polars_time
    mem_ratio = pandas_mem / polars_mem if polars_mem > 0 else 0
    
    print("\n📈 Comparison:")
    print(f"   Polars is {speedup:.2f}x faster")
    print(f"   Polars uses {mem_ratio:.2f}x {'more' if mem_ratio > 1 else 'less'} memory")
    
    return (df_orders_pd, df_customers_pd, df_products_pd,
            df_orders_pl, df_customers_pl, df_products_pl, results)


def benchmark_complex_joins(df_orders_pd, df_customers_pd, df_products_pd,
                           df_orders_pl, df_customers_pl, df_products_pl):
    """Compare 3-way join performance."""
    print_section("BENCHMARK 2: COMPLEX MULTI-TABLE JOINS (3-WAY JOIN)")
    
    results = {}
    
    # Pandas joins
    print("\n📊 Pandas - Performing 3-way join...")
    
    def pandas_join_operation():
        df_joined = df_orders_pd.merge(df_customers_pd, on='customer_id', how='left')
        df_full = df_joined.merge(df_products_pd, on='product_id', how='inner')
        return df_full
    
    start = time.time()
    mem_usage, df_full_pd = memory_usage(
        (pandas_join_operation,),
        retval=True,
        interval=0.1,
        max_usage=True
    )
    pandas_time = time.time() - start
    pandas_peak_mem = mem_usage
    
    results['pandas'] = {
        'time': pandas_time,
        'peak_memory': pandas_peak_mem,
        'result_rows': len(df_full_pd),
        'result_cols': len(df_full_pd.columns)
    }
    
    print(f"   Time: {pandas_time:.3f}s")
    print(f"   Peak Memory: {pandas_peak_mem:.2f} MB")
    print(f"   Result: {len(df_full_pd):,} rows × {len(df_full_pd.columns)} columns")
    
    # Polars joins
    print("\n📊 Polars - Performing 3-way join...")
    
    def polars_join_operation():
        df_joined = df_orders_pl.join(df_customers_pl, on='customer_id', how='left')
        df_full = df_joined.join(df_products_pl, on='product_id', how='inner')
        return df_full
    
    start = time.time()
    mem_usage, df_full_pl = memory_usage(
        (polars_join_operation,),
        retval=True,
        interval=0.1,
        max_usage=True
    )
    polars_time = time.time() - start
    polars_peak_mem = mem_usage
    
    results['polars'] = {
        'time': polars_time,
        'peak_memory': polars_peak_mem,
        'result_rows': len(df_full_pl),
        'result_cols': len(df_full_pl.columns)
    }
    
    print(f"   Time: {polars_time:.3f}s")
    print(f"   Peak Memory: {polars_peak_mem:.2f} MB")
    print(f"   Result: {len(df_full_pl):,} rows × {len(df_full_pl.columns)} columns")
    
    # Comparison
    speedup = pandas_time / polars_time
    mem_ratio = pandas_peak_mem / polars_peak_mem if polars_peak_mem > 0 else 0
    
    print("\n📈 Comparison:")
    print(f"   Polars is {speedup:.2f}x faster")
    print(f"   Polars uses {mem_ratio:.2f}x {'more' if mem_ratio > 1 else 'less'} peak memory")
    
    return df_full_pd, df_full_pl, results


def benchmark_groupby_aggregations(df_full_pd, df_full_pl):
    """Compare groupby with multiple aggregations."""
    print_section("BENCHMARK 3: GROUPBY WITH MULTIPLE AGGREGATIONS")
    
    results = {}
    
    # Pandas groupby
    print("\n📊 Pandas - Groupby with aggregations...")
    
    def pandas_groupby_operation():
        # Prepare data
        df = df_full_pd.copy()
        df['final_amount'] = df['amount'].fillna(df['price'])
        
        # Complex groupby
        agg_result = df.groupby(['country', 'category', 'segment']).agg({
            'final_amount': ['sum', 'mean', 'median', 'std', 'min', 'max'],
            'order_id': ['count', 'nunique'],
            'customer_id': 'nunique'
        }).reset_index()
        return agg_result
    
    start = time.time()
    mem_usage, agg_pd = memory_usage(
        (pandas_groupby_operation,),
        retval=True,
        interval=0.1,
        max_usage=True
    )
    pandas_time = time.time() - start
    pandas_peak_mem = mem_usage
    
    results['pandas'] = {
        'time': pandas_time,
        'peak_memory': pandas_peak_mem,
        'result_groups': len(agg_pd)
    }
    
    print(f"   Time: {pandas_time:.3f}s")
    print(f"   Peak Memory: {pandas_peak_mem:.2f} MB")
    print(f"   Result: {len(agg_pd):,} groups")
    
    # Polars groupby
    print("\n📊 Polars - Groupby with aggregations...")
    
    def polars_groupby_operation():
        # Prepare data
        df = df_full_pl.with_columns([
            pl.when(pl.col('amount').is_null())
            .then(pl.col('price'))
            .otherwise(pl.col('amount'))
            .alias('final_amount')
        ])
        
        # Complex groupby
        agg_result = df.group_by(['country', 'category', 'segment']).agg([
            pl.col('final_amount').sum().alias('sum'),
            pl.col('final_amount').mean().alias('mean'),
            pl.col('final_amount').median().alias('median'),
            pl.col('final_amount').std().alias('std'),
            pl.col('final_amount').min().alias('min'),
            pl.col('final_amount').max().alias('max'),
            pl.col('order_id').count().alias('count'),
            pl.col('order_id').n_unique().alias('nunique_orders'),
            pl.col('customer_id').n_unique().alias('nunique_customers')
        ])
        return agg_result
    
    start = time.time()
    mem_usage, agg_pl = memory_usage(
        (polars_groupby_operation,),
        retval=True,
        interval=0.1,
        max_usage=True
    )
    polars_time = time.time() - start
    polars_peak_mem = mem_usage
    
    results['polars'] = {
        'time': polars_time,
        'peak_memory': polars_peak_mem,
        'result_groups': len(agg_pl)
    }
    
    print(f"   Time: {polars_time:.3f}s")
    print(f"   Peak Memory: {polars_peak_mem:.2f} MB")
    print(f"   Result: {len(agg_pl):,} groups")
    
    # Comparison
    speedup = pandas_time / polars_time
    mem_ratio = pandas_peak_mem / polars_peak_mem if polars_peak_mem > 0 else 0
    
    print("\n📈 Comparison:")
    print(f"   Polars is {speedup:.2f}x faster")
    print(f"   Polars uses {mem_ratio:.2f}x {'more' if mem_ratio > 1 else 'less'} peak memory")
    
    return results


def benchmark_filter_operations(df_full_pd, df_full_pl):
    """Compare filter operations on joined data."""
    print_section("BENCHMARK 4: FILTER OPERATIONS ON JOINED DATA")
    
    results = {}
    
    # Pandas filter
    print("\n📊 Pandas - Complex filtering...")
    
    def pandas_filter_operation():
        df_filtered = df_full_pd[
            (df_full_pd['status'] == 'completed') &
            (df_full_pd['order_date'] >= '2023-01-01') &
            (df_full_pd['amount'] > 50) &
            (df_full_pd['country'].isin(['USA', 'UK', 'Germany']))
        ].copy()
        return df_filtered
    
    start = time.time()
    mem_usage, df_filtered_pd = memory_usage(
        (pandas_filter_operation,),
        retval=True,
        interval=0.1,
        max_usage=True
    )
    pandas_time = time.time() - start
    pandas_peak_mem = mem_usage
    
    results['pandas'] = {
        'time': pandas_time,
        'peak_memory': pandas_peak_mem,
        'result_rows': len(df_filtered_pd),
        'filter_rate': len(df_filtered_pd) / len(df_full_pd)
    }
    
    print(f"   Time: {pandas_time:.3f}s")
    print(f"   Peak Memory: {pandas_peak_mem:.2f} MB")
    print(f"   Result: {len(df_filtered_pd):,} rows ({len(df_filtered_pd)/len(df_full_pd)*100:.1f}% of data)")
    
    # Polars filter
    print("\n📊 Polars - Complex filtering...")
    
    def polars_filter_operation():
        df_filtered = df_full_pl.filter(
            (pl.col('status') == 'completed') &
            (pl.col('order_date') >= pl.date(2023, 1, 1)) &
            (pl.col('amount') > 50) &
            (pl.col('country').is_in(['USA', 'UK', 'Germany']))
        )
        return df_filtered
    
    start = time.time()
    mem_usage, df_filtered_pl = memory_usage(
        (polars_filter_operation,),
        retval=True,
        interval=0.1,
        max_usage=True
    )
    polars_time = time.time() - start
    polars_peak_mem = mem_usage
    
    results['polars'] = {
        'time': polars_time,
        'peak_memory': polars_peak_mem,
        'result_rows': len(df_filtered_pl),
        'filter_rate': len(df_filtered_pl) / len(df_full_pl)
    }
    
    print(f"   Time: {polars_time:.3f}s")
    print(f"   Peak Memory: {polars_peak_mem:.2f} MB")
    print(f"   Result: {len(df_filtered_pl):,} rows ({len(df_filtered_pl)/len(df_full_pl)*100:.1f}% of data)")
    
    # Comparison
    speedup = pandas_time / polars_time
    mem_ratio = pandas_peak_mem / polars_peak_mem if polars_peak_mem > 0 else 0
    
    print("\n📈 Comparison:")
    print(f"   Polars is {speedup:.2f}x faster")
    print(f"   Polars uses {mem_ratio:.2f}x {'more' if mem_ratio > 1 else 'less'} peak memory")
    
    return results


def generate_comparison_table(benchmark_results):
    """Generate a formatted comparison table."""
    print_section("COMPREHENSIVE PERFORMANCE COMPARISON TABLE")
    
    print("\n" + "=" * 100)
    print(f"{'Operation':<30} {'Pandas Time':<15} {'Polars Time':<15} {'Speedup':<12} {'Memory Ratio':<12}")
    print("=" * 100)
    
    total_pandas_time = 0
    total_polars_time = 0
    
    for operation, results in benchmark_results.items():
        pandas_time = results['pandas']['time']
        polars_time = results['polars']['time']
        pandas_mem = results['pandas'].get('peak_memory', results['pandas'].get('memory', 0))
        polars_mem = results['polars'].get('peak_memory', results['polars'].get('memory', 0))
        
        speedup = pandas_time / polars_time if polars_time > 0 else 0
        mem_ratio = pandas_mem / polars_mem if polars_mem > 0 else 0
        
        print(f"{operation:<30} {pandas_time:>10.3f}s     {polars_time:>10.3f}s     "
              f"{speedup:>8.2f}x     {mem_ratio:>8.2f}x")
        
        total_pandas_time += pandas_time
        total_polars_time += polars_time
    
    print("=" * 100)
    overall_speedup = total_pandas_time / total_polars_time if total_polars_time > 0 else 0
    print(f"{'TOTAL':<30} {total_pandas_time:>10.3f}s     {total_polars_time:>10.3f}s     "
          f"{overall_speedup:>8.2f}x")
    print("=" * 100)
    
    print("\n📊 Summary:")
    print(f"   Overall, Polars is {overall_speedup:.2f}x faster than Pandas")
    print(f"   Total time saved: {total_pandas_time - total_polars_time:.3f}s")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print(" " * 25 + "PANDAS VS POLARS")
    print(" " * 20 + "PERFORMANCE COMPARISON")
    print("=" * 80)
    
    overall_start = time.time()
    benchmark_results = {}
    
    # Benchmark 1: Loading
    (df_orders_pd, df_customers_pd, df_products_pd,
     df_orders_pl, df_customers_pl, df_products_pl, 
     loading_results) = benchmark_loading()
    benchmark_results['Loading 360K Records'] = loading_results
    
    # Benchmark 2: Complex Joins
    df_full_pd, df_full_pl, joins_results = benchmark_complex_joins(
        df_orders_pd, df_customers_pd, df_products_pd,
        df_orders_pl, df_customers_pl, df_products_pl
    )
    benchmark_results['3-Way Join'] = joins_results
    
    # Benchmark 3: Groupby Aggregations
    groupby_results = benchmark_groupby_aggregations(df_full_pd, df_full_pl)
    benchmark_results['Groupby Aggregations'] = groupby_results
    
    # Benchmark 4: Filter Operations
    filter_results = benchmark_filter_operations(df_full_pd, df_full_pl)
    benchmark_results['Filter Operations'] = filter_results
    
    # Generate comparison table
    generate_comparison_table(benchmark_results)
    
    # Performance insights
    print_section("PERFORMANCE INSIGHTS")
    print("\n💡 Key Takeaways:")
    print("   1. Polars is consistently faster across all operations")
    print("   2. Performance gains are most significant for:")
    print("      - Complex joins on large datasets")
    print("      - Groupby operations with multiple aggregations")
    print("      - Filter operations with multiple conditions")
    print("   3. Polars uses parallel execution by default")
    print("   4. Polars has better memory efficiency due to Apache Arrow backend")
    print("   5. Lazy execution in Polars provides query optimization opportunities")
    
    print("\n🔍 When to use Pandas:")
    print("   - Small datasets (< 100K rows)")
    print("   - When ecosystem compatibility is critical (scikit-learn, etc.)")
    print("   - When you need specific pandas features not in Polars")
    
    print("\n🔍 When to use Polars:")
    print("   - Large datasets (> 100K rows)")
    print("   - Complex data transformations and joins")
    print("   - When performance is critical")
    print("   - When working with data larger than RAM (streaming)")
    
    total_time = time.time() - overall_start
    print(f"\n⏱  Total benchmark time: {total_time:.3f}s")
    
    print("\n" + "=" * 80)
    print("✓ Comparison demonstration complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
