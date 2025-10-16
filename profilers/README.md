# Pandas and Polars Profiling Project

A comprehensive hands-on project to learn and compare pandas and polars performance with complex operations on 300K+ records, featuring detailed profiling with py-spy, memory-profiler, and ydata-profiling.

## 🚀 Quick Start

### One-Command Setup and Run

```bash
# Setup virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate sample data
python sample_data.py

# Run all demos
python pandas_profiling_demo.py
python polars_profiling_demo.py
python comparison_demo.py
```

### Quick Demo (30 minutes)

```bash
# 1. Generate data (2 min)
python sample_data.py

# 2. Pandas demo with memory profiling (5 min)
python -m memory_profiler pandas_profiling_demo.py

# 3. Polars demo with lazy execution (5 min)
python polars_profiling_demo.py

# 4. Side-by-side comparison (5 min)
python comparison_demo.py

# 5. Generate flame graphs with py-spy (10 min)
py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py
py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

# 6. Open reports
open pandas_profile_report.html  # ydata-profiling report
open pandas_profile.svg           # py-spy flame graph
open polars_profile.svg           # py-spy flame graph
```

## 📁 Project Structure

```
profilers/
├── sample_data.py              # Generate 300K orders + customers + products
├── pandas_profiling_demo.py    # Pandas demo with memory profiling
├── polars_profiling_demo.py    # Polars demo with lazy execution
├── comparison_demo.py          # Side-by-side performance comparison
├── py_spy_instructions.md      # Detailed py-spy profiling guide
├── requirements.txt            # All dependencies
├── README.md                   # This file
└── data/                       # Generated datasets (CSV + Parquet)
    ├── orders.csv
    ├── orders.parquet
    ├── customers.csv
    ├── customers.parquet
    ├── products.csv
    └── products.parquet
```

## 📊 Datasets

### Orders Table (300K rows)

-   `order_id`: Unique order identifier
-   `customer_id`: Foreign key to customers
-   `product_id`: Foreign key to products
-   `order_date`: Date range 2020-2025
-   `amount`: Order amount with ~5% missing values
-   `status`: completed, pending, cancelled, shipped, returned

### Customers Table (50K rows)

-   `customer_id`: Unique customer identifier
-   `name`: Customer name
-   `country`: 10 countries with realistic distribution
-   `segment`: Premium, Standard, Basic, VIP
-   `registration_date`: Registration date with ~5% missing values

### Products Table (10K rows)

-   `product_id`: Unique product identifier
-   `category`: Electronics, Clothing, Home, Sports, Books
-   `subcategory`: Specific product types
-   `price`: Product price with ~5% missing values
-   `stock_level`: Current inventory

**Total Dataset Size**: ~360K rows, realistic e-commerce data with missing values

## 🔬 What Each Demo Shows

### 1. sample_data.py

**Purpose**: Generate realistic datasets for profiling

**Features**:

-   Creates 3 related tables with foreign keys
-   Includes realistic distributions and missing values
-   Saves in both CSV and Parquet formats
-   Shows memory usage statistics

**Runtime**: ~30 seconds

### 2. pandas_profiling_demo.py

**Purpose**: Demonstrate pandas operations with memory profiling

**Key Operations**:

-   Load 360K records from Parquet
-   3-way join: orders ← customers ← products
-   Left join + inner join combinations
-   Data enrichment and missing value handling
-   Complex filters (status, date range)
-   Multi-level groupby aggregations
-   ydata-profiling HTML report generation

**Profiling Tools**:

-   `@profile` decorator for line-by-line memory tracking
-   Execution time tracking for each operation
-   ydata-profiling for comprehensive dataset analysis

**Expected Runtime**: 15-30 seconds (+ 2-3 min for HTML report)

**Output**:

-   Console: Detailed timing and memory metrics
-   `pandas_profile_report.html`: Comprehensive dataset analysis

### 3. polars_profiling_demo.py

**Purpose**: Demonstrate polars with lazy execution and query optimization

**Key Operations**:

-   Lazy loading with `scan_parquet()`
-   Same 3-way joins as pandas demo
-   Query optimization with `.profile()`
-   Lazy vs eager execution comparison
-   Streaming execution for large datasets
-   Complex aggregations with multiple functions

**Profiling Tools**:

-   `.profile()` method for query plan analysis
-   Timing breakdown for each execution mode
-   Memory usage comparison

**Expected Runtime**: 5-10 seconds

**Output**:

-   Console: Query execution plan and timing details
-   Performance comparison: lazy vs eager

### 4. comparison_demo.py

**Purpose**: Side-by-side performance comparison

**Benchmarks**:

1. **Loading 360K records**: Parquet loading performance
2. **3-way join**: Complex multi-table joins
3. **Groupby aggregations**: Multiple aggregation functions
4. **Filter operations**: Complex filtering on joined data

**Profiling Tools**:

-   `memory_profiler.memory_usage()` for peak memory tracking
-   Detailed timing for each operation
-   Comparison table generation

**Expected Runtime**: 20-40 seconds

**Output**:

-   Comprehensive comparison table
-   Speed-up ratios (Polars vs Pandas)
-   Memory usage ratios
-   Performance insights

## 📈 Interpreting Profiler Outputs

### Memory Profiler (@profile decorator)

**Read the output**:

```
Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    45     180.2 MiB     180.2 MiB           1   @profile
    46                                           def perform_complex_joins():
    47     280.5 MiB     100.3 MiB           1       df_joined = df_orders.merge(...)
    48     420.8 MiB     140.3 MiB           1       df_full = df_joined.merge(...)
```

**Key Columns**:

-   **Mem usage**: Total memory at this point
-   **Increment**: Memory added by this line
-   **Line Contents**: The actual code

**What to look for**:

-   Large increments indicate memory-intensive operations
-   Peak memory usage for capacity planning
-   Memory not released (potential memory leaks)

### ydata-profiling Report

**Sections**:

1. **Overview**: Dataset summary, variables, observations, missing cells
2. **Variables**: Distribution, statistics for each column
3. **Correlations**: Pearson, Spearman, Cramér's V matrices
4. **Missing values**: Patterns and counts
5. **Sample**: First/last rows preview

**Use cases**:

-   Data quality assessment
-   Finding outliers and anomalies
-   Understanding distributions before modeling
-   Identifying correlations

### Polars .profile() Output

**Read the output**:

```
╭────────────────────────┬────────┬────────────╮
│ node                   │ time   │ % of total │
├────────────────────────┼────────┼────────────┤
│ SCAN orders.parquet    │ 0.05s  │ 5%         │
│ JOIN customers         │ 0.30s  │ 30%        │
│ JOIN products          │ 0.25s  │ 25%        │
│ FILTER                 │ 0.10s  │ 10%        │
│ COLLECT               │ 0.30s  │ 30%        │
╰────────────────────────┴────────┴────────────╯
```

**Key Insights**:

-   Shows query execution plan
-   Time spent in each operation
-   Helps identify bottlenecks
-   Validates query optimization

### py-spy Flame Graphs

**How to read** (see `py_spy_instructions.md` for details):

-   **Width**: Time spent in function (wider = more time)
-   **Height**: Call stack depth
-   **Colors**: Random (for differentiation only)

**What to look for**:

-   Wide bars = bottlenecks (optimization targets)
-   Compare pandas vs polars widths
-   Look for unexpected wide bars
-   Check Python vs native code time (Polars)

**Example findings**:

-   Pandas `merge()` should be wider than Polars `join()`
-   Polars spends more time in native (Rust) code
-   `groupby.agg()` comparison shows Polars efficiency

## ⚡ Expected Performance Results

### Typical Benchmarks (300K records)

| Operation            | Pandas   | Polars       | Speedup  |
| -------------------- | -------- | ------------ | -------- |
| Loading 360K rows    | 0.8-1.2s | 0.3-0.5s     | 2-3x     |
| 3-way join           | 2.5-3.5s | 0.8-1.2s     | 2.5-3x   |
| Groupby aggregations | 1.0-1.5s | 0.3-0.5s     | 3-4x     |
| Filter operations    | 0.5-0.8s | 0.1-0.2s     | 4-5x     |
| **Total**            | **5-7s** | **1.5-2.5s** | **3-4x** |

**Memory Usage**:

-   Pandas: 200-300 MB peak
-   Polars: 150-200 MB peak
-   Polars is ~1.5x more memory efficient

**Note**: Results vary based on hardware (CPU cores, RAM, disk speed)

## 🎯 Key Performance Differences

### Why Polars is Faster

1. **Apache Arrow Backend**

    - Columnar memory format
    - Zero-copy data sharing
    - Cache-friendly operations

2. **Parallel Execution**

    - Automatic multi-threading
    - Exploits all CPU cores
    - No GIL limitations

3. **Lazy Evaluation**

    - Query optimization before execution
    - Predicate pushdown (filter early)
    - Projection pushdown (select only needed columns)

4. **Rust Implementation**

    - Compiled language (vs Python)
    - Better memory management
    - SIMD optimizations

5. **Streaming Execution**
    - Process data in chunks
    - Handle datasets larger than RAM
    - Reduced memory footprint

### When Pandas Wins

1. **Small datasets** (< 100K rows)

    - Overhead doesn't matter
    - Familiar syntax

2. **Ecosystem integration**

    - scikit-learn, statsmodels
    - matplotlib, seaborn
    - Jupyter notebooks

3. **Specialized operations**
    - Some pandas-only functions
    - More mature feature set

## 🔍 Memory Profiling Tips

### Identifying Bottlenecks

1. **Memory Spikes**: Look for large increments in memory profiler

    ```python
    # Bad: Creates intermediate copy
    df = df[df['amount'] > 100]  # +50 MB
    df = df[df['status'] == 'completed']  # +50 MB

    # Good: Single operation
    df = df[(df['amount'] > 100) & (df['status'] == 'completed')]  # +50 MB
    ```

2. **Memory Not Released**: Track memory after operations

    ```python
    # If memory doesn't drop, you have references
    import gc
    gc.collect()  # Force garbage collection
    ```

3. **Join Explosion**: Monitor joined dataframe size
    ```python
    # If result >> input sizes, check join keys
    print(f"Orders: {len(df_orders):,}")
    print(f"Joined: {len(df_joined):,}")
    # If joined > orders, you have duplicate keys!
    ```

### Optimization Strategies

1. **Use appropriate data types**

    ```python
    # Pandas: Convert strings to category
    df['status'] = df['status'].astype('category')

    # Polars: Automatically optimizes types
    df = pl.read_parquet('data.parquet')
    ```

2. **Chunk large operations**

    ```python
    # Pandas: Process in chunks
    for chunk in pd.read_csv('large.csv', chunksize=10000):
        process(chunk)

    # Polars: Use streaming
    result = pl.scan_csv('large.csv').collect(streaming=True)
    ```

3. **Filter early**

    ```python
    # Bad: Filter after join
    df_joined = orders.merge(customers)
    df_filtered = df_joined[df_joined['date'] > '2023-01-01']

    # Good: Filter before join
    orders_filtered = orders[orders['date'] > '2023-01-01']
    df_joined = orders_filtered.merge(customers)
    ```

## 🛠️ Troubleshooting

### Common Issues

1. **Memory profiler not showing output**

    ```bash
    # Make sure to run with -m flag
    python -m memory_profiler pandas_profiling_demo.py
    ```

2. **py-spy permission denied**

    ```bash
    # On macOS, you may need to disable SIP or run with sudo
    sudo py-spy record -o profile.svg -- python script.py
    ```

3. **ydata-profiling taking too long**

    ```python
    # Use minimal mode for faster report
    profile = ProfileReport(df, minimal=True)
    ```

4. **Out of memory errors**
    ```python
    # Reduce dataset size or use streaming
    # In sample_data.py, reduce n_orders to 100_000
    ```

## 📚 Additional Resources

### Documentation

-   [Pandas Documentation](https://pandas.pydata.org/docs/)
-   [Polars Documentation](https://pola-rs.github.io/polars/)
-   [ydata-profiling](https://github.com/ydataai/ydata-profiling)
-   [memory-profiler](https://github.com/pythonprofilers/memory_profiler)
-   [py-spy](https://github.com/benfred/py-spy)

### Learning Resources

-   [Polars vs Pandas Comparison](https://www.rhosignal.com/posts/polars-pandas-cheatsheet/)
-   [Apache Arrow Format](https://arrow.apache.org/)
-   [Flame Graphs Explained](http://www.brendangregg.com/flamegraphs.html)

### Next Steps

1. Try with your own datasets
2. Experiment with different join types
3. Profile your actual use cases
4. Learn Polars lazy execution patterns
5. Optimize memory-intensive operations

## 📝 Notes

-   All scripts are self-contained and can run independently
-   Data is generated once and reused by all demos
-   Parquet format is faster and more efficient than CSV
-   Results vary based on hardware (CPU cores, RAM, disk speed)
-   Memory profiler adds overhead (~30% slower)
-   py-spy has minimal overhead (~1-2% slower)

## 🤝 Contributing

Feel free to:

-   Add more complex operations
-   Test with different dataset sizes
-   Implement additional profiling techniques
-   Share optimization tips

---

**Happy Profiling! 🚀**
