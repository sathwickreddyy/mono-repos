#!/usr/bin/env python3
"""
Quick 2-minute benchmark: Pandas vs Polars on a simple operation.
Perfect for a quick demo of the performance difference.
"""

import pandas as pd
import polars as pl
import time
from pathlib import Path


def benchmark_pandas():
    """Benchmark pandas: load + join + group."""
    data_dir = Path('data')
    
    start = time.time()
    
    # Load
    df_orders = pd.read_parquet(data_dir / 'orders.parquet')
    df_customers = pd.read_parquet(data_dir / 'customers.parquet')
    
    # Join
    df_joined = df_orders.merge(df_customers, on='customer_id', how='left')
    
    # Aggregate
    result = df_joined.groupby('country').agg({
        'amount': ['sum', 'mean', 'count'],
        'order_id': 'count'
    })
    
    elapsed = time.time() - start
    return elapsed, len(result)


def benchmark_polars():
    """Benchmark polars: load + join + group."""
    data_dir = Path('data')
    
    start = time.time()
    
    # Load
    df_orders = pl.read_parquet(data_dir / 'orders.parquet')
    df_customers = pl.read_parquet(data_dir / 'customers.parquet')
    
    # Join
    df_joined = df_orders.join(df_customers, on='customer_id', how='left')
    
    # Aggregate
    result = df_joined.group_by('country').agg([
        pl.col('amount').sum().alias('sum'),
        pl.col('amount').mean().alias('mean'),
        pl.col('amount').count().alias('count'),
        pl.col('order_id').count().alias('order_count')
    ])
    
    elapsed = time.time() - start
    return elapsed, len(result)


def benchmark_polars_lazy():
    """Benchmark polars with lazy execution: load + join + group."""
    data_dir = Path('data')
    
    start = time.time()
    
    # Lazy load and execute entire pipeline
    result = (
        pl.scan_parquet(data_dir / 'orders.parquet')
        .join(
            pl.scan_parquet(data_dir / 'customers.parquet'),
            on='customer_id',
            how='left'
        )
        .group_by('country')
        .agg([
            pl.col('amount').sum().alias('sum'),
            pl.col('amount').mean().alias('mean'),
            pl.col('amount').count().alias('count'),
            pl.col('order_id').count().alias('order_count')
        ])
        .collect()
    )
    
    elapsed = time.time() - start
    return elapsed, len(result)


def main():
    print("\n" + "=" * 70)
    print(" " * 15 + "PANDAS vs POLARS: QUICK BENCHMARK")
    print("=" * 70)
    
    print("\n📊 Operation: Load 300K orders + 50K customers → Join → Group by country\n")
    
    # Run benchmarks
    print("Running Pandas benchmark...")
    pandas_time, pandas_rows = benchmark_pandas()
    
    print("Running Polars (eager) benchmark...")
    polars_time, polars_rows = benchmark_polars()
    
    print("Running Polars (lazy) benchmark...")
    polars_lazy_time, polars_lazy_rows = benchmark_polars_lazy()
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\n{'Library':<20} {'Time (s)':<15} {'Result Rows':<15} {'Speedup':<15}")
    print("-" * 70)
    print(f"{'Pandas':<20} {pandas_time:>10.3f}s     {pandas_rows:>10}      {'1.00x':<15}")
    print(f"{'Polars (eager)':<20} {polars_time:>10.3f}s     {polars_rows:>10}      {pandas_time/polars_time:>10.2f}x")
    print(f"{'Polars (lazy)':<20} {polars_lazy_time:>10.3f}s     {polars_lazy_rows:>10}      {pandas_time/polars_lazy_time:>10.2f}x")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    
    best_time = min(polars_time, polars_lazy_time)
    best_name = "Polars (lazy)" if polars_lazy_time < polars_time else "Polars (eager)"
    overall_speedup = pandas_time / best_time
    
    print(f"\n✓ {best_name} is {overall_speedup:.2f}x faster than Pandas")
    print(f"✓ Time saved: {pandas_time - best_time:.3f} seconds")
    print(f"✓ For 300K records: {(pandas_time - best_time) * 1000 / 300:.2f}ms per 1K records saved")
    
    if polars_lazy_time < polars_time:
        lazy_improvement = (polars_time / polars_lazy_time - 1) * 100
        print(f"\n💡 Lazy execution is {lazy_improvement:.1f}% faster than eager (query optimization!)")
    
    print("\n📚 Want to learn more? Run:")
    print("   python run_all_demos.py")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
