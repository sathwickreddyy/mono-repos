# Pandas & Polars Scaling Analysis with Profilers# Pandas and Polars Profiling Project



A focused project for analyzing pandas and polars performance at scale using **memory-profiler** and **py-spy**.A comprehensive hands-on project to learn and compare pandas and polars performance with complex operations on 300K+ records, featuring detailed profiling with py-spy, memory-profiler, and ydata-profiling.



## 🎯 Project Focus## 🚀 Quick Start



This project uses **2 essential profilers** for scaling analysis:### One-Command Setup and Run

1. **memory-profiler** - Track RAM usage and identify memory bottlenecks

2. **py-spy** - Visualize CPU time and find performance bottlenecks```bash

# Setup virtual environment and install dependencies

## 🚀 Quick Startpython3 -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

```bashpip install -r requirements.txt

# 1. Setup (one-time)

source venv/bin/activate  # Already created# Generate sample data

pip install -r requirements.txtpython sample_data.py



# 2. Generate sample data# Run all demos

python sample_data.pypython pandas_profiling_demo.py

python polars_profiling_demo.py

# 3. Run demos with profilingpython comparison_demo.py

python -m memory_profiler pandas_profiling_demo.py```

python -m memory_profiler polars_profiling_demo.py

python -m memory_profiler comparison_demo.py### Quick Demo (30 minutes)



# 4. Generate flame graphs```bash

py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py# 1. Generate data (2 min)

py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.pypython sample_data.py



# 5. View results# 2. Pandas demo with memory profiling (5 min)

open pandas_profile.svgpython -m memory_profiler pandas_profiling_demo.py

open polars_profile.svg

```# 3. Polars demo with lazy execution (5 min)

python polars_profiling_demo.py

## 📊 The Two Essential Profilers

# 4. Side-by-side comparison (5 min)

### 1. memory-profiler (RAM Analysis)python comparison_demo.py



**What it does:** Shows memory usage line-by-line# 5. Generate flame graphs with py-spy (10 min)

py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py

**Why it's essential for scaling:**py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

- Identifies memory leaks before they crash production

- Shows which operations consume most RAM# 6. Open reports

- Helps predict memory needs for larger datasetsopen pandas_profile_report.html  # ydata-profiling report

- Catches memory growth patternsopen pandas_profile.svg           # py-spy flame graph

open polars_profile.svg           # py-spy flame graph

**How to use:**```

```bash

python -m memory_profiler script.py## 📁 Project Structure

```

```

**What you get:**profilers/

```├── sample_data.py              # Generate 300K orders + customers + products

Line #    Mem usage    Increment  Line Contents├── pandas_profiling_demo.py    # Pandas demo with memory profiling

================================================├── polars_profiling_demo.py    # Polars demo with lazy execution

    49     280.5 MiB   100.3 MiB     df_joined = df_orders.merge(...)├── comparison_demo.py          # Side-by-side performance comparison

    50     420.8 MiB   140.3 MiB     df_full = df_joined.merge(...)├── py_spy_instructions.md      # Detailed py-spy profiling guide

```├── requirements.txt            # All dependencies

├── README.md                   # This file

**Key metrics for scaling:**└── data/                       # Generated datasets (CSV + Parquet)

- Peak memory usage    ├── orders.csv

- Memory per row (scale linearly)    ├── orders.parquet

- Memory growth rate    ├── customers.csv

- Whether memory is released    ├── customers.parquet

    ├── products.csv

### 2. py-spy (CPU Analysis)    └── products.parquet

```

**What it does:** Creates flame graphs showing where CPU time is spent

## 📊 Datasets

**Why it's essential for scaling:**

- Identifies performance bottlenecks### Orders Table (300K rows)

- Shows which functions to optimize first

- Reveals parallelization opportunities-   `order_id`: Unique order identifier

- Compares implementations visually-   `customer_id`: Foreign key to customers

-   `product_id`: Foreign key to products

**How to use:**-   `order_date`: Date range 2020-2025

```bash-   `amount`: Order amount with ~5% missing values

py-spy record -o profile.svg -- python script.py-   `status`: completed, pending, cancelled, shipped, returned

open profile.svg

```### Customers Table (50K rows)



**What you get:** Interactive SVG flame graph where:-   `customer_id`: Unique customer identifier

- **Width** = Time spent (wider = slower)-   `name`: Customer name

- **Height** = Call stack depth-   `country`: 10 countries with realistic distribution

- Click to zoom, hover for details-   `segment`: Premium, Standard, Basic, VIP

-   `registration_date`: Registration date with ~5% missing values

**Key metrics for scaling:**

- Total execution time### Products Table (10K rows)

- Time per function

- Sequential vs parallel execution-   `product_id`: Unique product identifier

- Python overhead vs native code-   `category`: Electronics, Clothing, Home, Sports, Books

-   `subcategory`: Specific product types

## 📁 Project Structure-   `price`: Product price with ~5% missing values

-   `stock_level`: Current inventory

```

profilers/**Total Dataset Size**: ~360K rows, realistic e-commerce data with missing values

├── sample_data.py              # Generate datasets (100K - 1M rows)

├── pandas_profiling_demo.py    # Pandas with @profile decorators## 🔬 What Each Demo Shows

├── polars_profiling_demo.py    # Polars with @profile decorators

├── comparison_demo.py          # Side-by-side comparison### 1. sample_data.py

├── scaling_analysis.py         # Scaling analysis tool

├── requirements.txt            # Minimal dependencies**Purpose**: Generate realistic datasets for profiling

└── data/                       # Generated datasets

```**Features**:



## 🔬 Scaling Analysis Workflow-   Creates 3 related tables with foreign keys

-   Includes realistic distributions and missing values

### Step 1: Profile at Current Scale-   Saves in both CSV and Parquet formats

```bash-   Shows memory usage statistics

# Generate 300K records

python sample_data.py**Runtime**: ~30 seconds



# Profile memory### 2. pandas_profiling_demo.py

python -m memory_profiler comparison_demo.py > profile_300k_memory.txt

**Purpose**: Demonstrate pandas operations with memory profiling

# Profile CPU

py-spy record -o profile_300k.svg -- python comparison_demo.py**Key Operations**:

```

-   Load 360K records from Parquet

### Step 2: Profile at Target Scale-   3-way join: orders ← customers ← products

```bash-   Left join + inner join combinations

# Edit sample_data.py: n_orders=1_000_000-   Data enrichment and missing value handling

python sample_data.py-   Complex filters (status, date range)

-   Multi-level groupby aggregations

# Profile memory-   ydata-profiling HTML report generation

python -m memory_profiler comparison_demo.py > profile_1m_memory.txt

**Profiling Tools**:

# Profile CPU

py-spy record -o profile_1m.svg -- python comparison_demo.py-   `@profile` decorator for line-by-line memory tracking

```-   Execution time tracking for each operation

-   ydata-profiling for comprehensive dataset analysis

### Step 3: Analyze Scaling Characteristics

```bash**Expected Runtime**: 15-30 seconds (+ 2-3 min for HTML report)

# Compare profiles

python scaling_analysis.py --compare profile_300k_memory.txt profile_1m_memory.txt**Output**:

```

-   Console: Detailed timing and memory metrics

**Key questions answered:**-   `pandas_profile_report.html`: Comprehensive dataset analysis

- Does memory scale linearly? (300K → 1M = 3.3x data)

- Does execution time scale linearly?### 3. polars_profiling_demo.py

- Where are the bottlenecks?

- Which library scales better?**Purpose**: Demonstrate polars with lazy execution and query optimization



## 📈 Interpreting Results for Scaling**Key Operations**:



### Memory Profiler Output-   Lazy loading with `scan_parquet()`

-   Same 3-way joins as pandas demo

**Look for:**-   Query optimization with `.profile()`

-   Lazy vs eager execution comparison

1. **Linear scaling** (Good):-   Streaming execution for large datasets

   ```-   Complex aggregations with multiple functions

   300K rows: 200 MB → 1M rows: 666 MB (3.3x)

   ```**Profiling Tools**:



2. **Super-linear scaling** (Bad):-   `.profile()` method for query plan analysis

   ```-   Timing breakdown for each execution mode

   300K rows: 200 MB → 1M rows: 2000 MB (10x!) ⚠️-   Memory usage comparison

   ```

**Expected Runtime**: 5-10 seconds

3. **Memory not released** (Critical):

   ```**Output**:

   Line 50: 420 MB

   Line 51: 420 MB  ← Memory should drop if data no longer needed-   Console: Query execution plan and timing details

   Line 52: 420 MB-   Performance comparison: lazy vs eager

   ```

### 4. comparison_demo.py

**Scaling predictions:**

```python**Purpose**: Side-by-side performance comparison

# If 300K rows = 200 MB and scaling is linear:

memory_per_row = 200 MB / 300_000 = 0.67 KB/row**Benchmarks**:

memory_for_10M = 0.67 KB/row * 10_000_000 = 6.7 GB

```1. **Loading 360K records**: Parquet loading performance

2. **3-way join**: Complex multi-table joins

### Flame Graph Analysis3. **Groupby aggregations**: Multiple aggregation functions

4. **Filter operations**: Complex filtering on joined data

**Look for:**

**Profiling Tools**:

1. **Wide bars** = Bottlenecks to optimize first

2. **Comparison:**-   `memory_profiler.memory_usage()` for peak memory tracking

   - Pandas: Wide merge() bars-   Detailed timing for each operation

   - Polars: Narrow bars, more time in native code-   Comparison table generation



3. **Parallelization opportunities:****Expected Runtime**: 20-40 seconds

   - Single wide bar = Could parallelize

   - Many parallel bars = Already parallelized**Output**:



**Scaling insights:**-   Comprehensive comparison table

```-   Speed-up ratios (Polars vs Pandas)

If pandas merge() takes 2s for 300K rows:-   Memory usage ratios

- Linear: 1M rows = 6.7s-   Performance insights

- But flame graph shows sequential execution

- Optimization: Switch to Polars for parallel execution## 📈 Interpreting Profiler Outputs

- Polars: 1M rows = 2s (3.3x faster!)

```### Memory Profiler (@profile decorator)



## 🎯 Scaling Analysis Scenarios**Read the output**:



### Scenario 1: Memory-Constrained Environment```

Line #    Mem usage    Increment  Occurences   Line Contents

**Goal:** Keep memory under 8GB for 10M rows============================================================

    45     180.2 MiB     180.2 MiB           1   @profile

**Approach:**    46                                           def perform_complex_joins():

```bash    47     280.5 MiB     100.3 MiB           1       df_joined = df_orders.merge(...)

# Test with increasing sizes    48     420.8 MiB     140.3 MiB           1       df_full = df_joined.merge(...)

python sample_data.py  # 300K rows```

python -m memory_profiler comparison_demo.py

**Key Columns**:

python sample_data.py  # 500K rows  

python -m memory_profiler comparison_demo.py-   **Mem usage**: Total memory at this point

-   **Increment**: Memory added by this line

python sample_data.py  # 1M rows-   **Line Contents**: The actual code

python -m memory_profiler comparison_demo.py

```**What to look for**:



**Analysis:**-   Large increments indicate memory-intensive operations

1. Plot memory vs rows-   Peak memory usage for capacity planning

2. Find scaling factor-   Memory not released (potential memory leaks)

3. Predict 10M row memory

4. If > 8GB, optimize:### ydata-profiling Report

   - Use Polars (lower memory)

   - Stream data in chunks**Sections**:

   - Use lazy evaluation

1. **Overview**: Dataset summary, variables, observations, missing cells

### Scenario 2: Time-Constrained Processing2. **Variables**: Distribution, statistics for each column

3. **Correlations**: Pearson, Spearman, Cramér's V matrices

**Goal:** Process 10M rows in under 5 minutes4. **Missing values**: Patterns and counts

5. **Sample**: First/last rows preview

**Approach:**

```bash**Use cases**:

# Profile execution time

py-spy record -o profile_300k.svg -- python comparison_demo.py-   Data quality assessment

py-spy record -o profile_1m.svg -- python comparison_demo.py-   Finding outliers and anomalies

```-   Understanding distributions before modeling

-   Identifying correlations

**Analysis:**

1. Compare flame graph widths### Polars .profile() Output

2. Calculate time scaling factor

3. Identify bottleneck functions**Read the output**:

4. Optimize widest bars first

```

### Scenario 3: Choosing Between Pandas and Polars╭────────────────────────┬────────┬────────────╮

│ node                   │ time   │ % of total │

**Goal:** Make data-driven decision for production├────────────────────────┼────────┼────────────┤

│ SCAN orders.parquet    │ 0.05s  │ 5%         │

**Metrics to compare:**│ JOIN customers         │ 0.30s  │ 30%        │

│ JOIN products          │ 0.25s  │ 25%        │

| Metric | Pandas | Polars | Winner |│ FILTER                 │ 0.10s  │ 10%        │

|--------|--------|--------|--------|│ COLLECT               │ 0.30s  │ 30%        │

| Memory @ 300K | 280 MB | 180 MB | Polars |╰────────────────────────┴────────┴────────────╯

| Memory @ 1M | 950 MB | 600 MB | Polars |```

| Time @ 300K | 5.2s | 1.8s | Polars |

| Time @ 1M | 18.5s | 6.1s | Polars |**Key Insights**:

| Scaling | Super-linear | Linear | Polars |

-   Shows query execution plan

## 🔧 Optimization Based on Profiling-   Time spent in each operation

-   Helps identify bottlenecks

### Memory Optimization-   Validates query optimization



**From memory-profiler output:**### py-spy Flame Graphs

```python

# Bad: Creates multiple copies**How to read** (see `py_spy_instructions.md` for details):

Line 49: 280 MB    df_joined = orders.merge(customers)  # +100 MB

Line 50: 420 MB    df_full = df_joined.merge(products)  # +140 MB-   **Width**: Time spent in function (wider = more time)

Line 51: 520 MB    df_filtered = df_full[condition]     # +100 MB-   **Height**: Call stack depth

-   **Colors**: Random (for differentiation only)

# Good: Filter early, reduce copies

Line 49: 180 MB    orders_filtered = orders[condition]  # +50 MB**What to look for**:

Line 50: 230 MB    df_joined = orders_filtered.merge(customers)  # +50 MB

Line 51: 280 MB    df_full = df_joined.merge(products)  # +50 MB-   Wide bars = bottlenecks (optimization targets)

```-   Compare pandas vs polars widths

-   Look for unexpected wide bars

### CPU Optimization-   Check Python vs native code time (Polars)



**From py-spy flame graph:****Example findings**:

```

Wide bar: merge() taking 60% of time-   Pandas `merge()` should be wider than Polars `join()`

→ Optimize: Use Polars for parallel merge-   Polars spends more time in native (Rust) code

→ Result: 60% → 15% (4x faster)-   `groupby.agg()` comparison shows Polars efficiency



Wide bar: groupby() taking 30% of time  ## ⚡ Expected Performance Results

→ Optimize: Use vectorized operations

→ Result: 30% → 10% (3x faster)### Typical Benchmarks (300K records)

```

| Operation            | Pandas   | Polars       | Speedup  |

## 📚 Essential Commands| -------------------- | -------- | ------------ | -------- |

| Loading 360K rows    | 0.8-1.2s | 0.3-0.5s     | 2-3x     |

```bash| 3-way join           | 2.5-3.5s | 0.8-1.2s     | 2.5-3x   |

# Memory profiling| Groupby aggregations | 1.0-1.5s | 0.3-0.5s     | 3-4x     |

python -m memory_profiler script.py > memory_report.txt| Filter operations    | 0.5-0.8s | 0.1-0.2s     | 4-5x     |

cat memory_report.txt | grep "MiB"  # See memory usage| **Total**            | **5-7s** | **1.5-2.5s** | **3-4x** |



# CPU profiling (basic)**Memory Usage**:

py-spy record -o profile.svg -- python script.py

open profile.svg-   Pandas: 200-300 MB peak

-   Polars: 150-200 MB peak

# CPU profiling (detailed, with native code)-   Polars is ~1.5x more memory efficient

py-spy record -o profile.svg -r 500 --native -- python script.py

**Note**: Results vary based on hardware (CPU cores, RAM, disk speed)

# Compare profiles

diff profile_300k_memory.txt profile_1m_memory.txt## 🎯 Key Performance Differences

```

### Why Polars is Faster

## 🎓 Learning Path

1. **Apache Arrow Backend**

**Day 1: Understanding the Profilers**

1. Read profiler sections in this README    - Columnar memory format

2. Run: `python quick_benchmark.py`    - Zero-copy data sharing

3. Run: `python -m memory_profiler pandas_profiling_demo.py`    - Cache-friendly operations

4. Understand memory output

2. **Parallel Execution**

**Day 2: Memory Analysis**

1. Generate data at different scales    - Automatic multi-threading

2. Profile each scale    - Exploits all CPU cores

3. Plot memory vs dataset size    - No GIL limitations

4. Calculate scaling factors

3. **Lazy Evaluation**

**Day 3: CPU Analysis**

1. Generate flame graphs for pandas    - Query optimization before execution

2. Generate flame graphs for polars    - Predicate pushdown (filter early)

3. Compare visually    - Projection pushdown (select only needed columns)

4. Identify bottlenecks

4. **Rust Implementation**

**Day 4: Optimization**

1. Implement fixes based on profiling    - Compiled language (vs Python)

2. Re-profile to measure improvement    - Better memory management

3. Document findings    - SIMD optimizations



## 💡 Pro Tips5. **Streaming Execution**

    - Process data in chunks

### Memory Profiling    - Handle datasets larger than RAM

✅ **DO:**    - Reduced memory footprint

- Profile with realistic data sizes

- Look for memory leaks (no drops)### When Pandas Wins

- Calculate memory per row

- Test at multiple scales1. **Small datasets** (< 100K rows)



❌ **DON'T:**    - Overhead doesn't matter

- Profile tiny datasets (overhead dominates)    - Familiar syntax

- Ignore gradual memory growth

- Assume linear scaling without testing2. **Ecosystem integration**



### CPU Profiling    - scikit-learn, statsmodels

✅ **DO:**    - matplotlib, seaborn

- Generate multiple flame graphs    - Jupyter notebooks

- Compare implementations side-by-side

- Focus on widest bars first3. **Specialized operations**

- Use `--native` for Polars/numpy code    - Some pandas-only functions

    - More mature feature set

❌ **DON'T:**

- Optimize before profiling## 🔍 Memory Profiling Tips

- Ignore Python overhead

- Profile debug mode code### Identifying Bottlenecks



## 🎯 Success Criteria for Scaling1. **Memory Spikes**: Look for large increments in memory profiler



**Memory:**    ```python

- ✅ Linear scaling (rows × constant)    # Bad: Creates intermediate copy

- ✅ Memory released after use    df = df[df['amount'] > 100]  # +50 MB

- ✅ Peak < available RAM at target scale    df = df[df['status'] == 'completed']  # +50 MB



**Performance:**    # Good: Single operation

- ✅ Sub-linear time scaling (with parallelization)    df = df[(df['amount'] > 100) & (df['status'] == 'completed')]  # +50 MB

- ✅ Bottlenecks identified and optimized    ```

- ✅ Meets SLA at target scale

2. **Memory Not Released**: Track memory after operations

**Decision Making:**

- ✅ Data-driven library choice    ```python

- ✅ Documented scaling characteristics    # If memory doesn't drop, you have references

- ✅ Predictable resource requirements    import gc

    gc.collect()  # Force garbage collection

## 📊 Example Scaling Analysis    ```



```bash3. **Join Explosion**: Monitor joined dataframe size

# Generate scaling report    ```python

python scaling_analysis.py    # If result >> input sizes, check join keys

    print(f"Orders: {len(df_orders):,}")

# Output:    print(f"Joined: {len(df_joined):,}")

# Dataset Size: 300K rows    # If joined > orders, you have duplicate keys!

# Pandas Memory: 280 MB (0.93 KB/row)    ```

# Polars Memory: 180 MB (0.60 KB/row)

# ### Optimization Strategies

# Dataset Size: 1M rows  

# Pandas Memory: 950 MB (0.95 KB/row) ✅ Linear1. **Use appropriate data types**

# Polars Memory: 600 MB (0.60 KB/row) ✅ Linear

#    ```python

# Prediction for 10M rows:    # Pandas: Convert strings to category

# Pandas: ~9.5 GB    df['status'] = df['status'].astype('category')

# Polars: ~6.0 GB

#    # Polars: Automatically optimizes types

# Recommendation: Use Polars for 37% memory savings    df = pl.read_parquet('data.parquet')

```    ```



## 🔗 Resources2. **Chunk large operations**



- [memory-profiler docs](https://github.com/pythonprofilers/memory_profiler)    ```python

- [py-spy docs](https://github.com/benfred/py-spy)    # Pandas: Process in chunks

- [Flame Graphs Explained](http://www.brendangregg.com/flamegraphs.html)    for chunk in pd.read_csv('large.csv', chunksize=10000):

        process(chunk)

---

    # Polars: Use streaming

**Focus: Memory + CPU profiling for data-driven scaling decisions** 🚀    result = pl.scan_csv('large.csv').collect(streaming=True)

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
