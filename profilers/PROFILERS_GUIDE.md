# PROFILERS EXPLAINED: What Does What and How to Use Them

## 📚 Table of Contents

1. [Overview of Profilers](#overview)
2. [memory-profiler](#memory-profiler)
3. [ydata-profiling](#ydata-profiling)
4. [py-spy](#py-spy)
5. [Polars .profile()](#polars-profile)
6. [When to Use Each](#when-to-use)
7. [Practical Examples](#practical-examples)

---

## Overview of Profilers {#overview}

This project includes **4 different profilers**, each serving a unique purpose:

| Profiler              | What It Profiles      | Output Format   | Use Case                             |
| --------------------- | --------------------- | --------------- | ------------------------------------ |
| **memory-profiler**   | RAM usage per line    | Text report     | Find memory leaks, optimize memory   |
| **ydata-profiling**   | Dataset statistics    | HTML report     | Data quality, EDA automation         |
| **py-spy**            | CPU time per function | SVG flame graph | Find slow functions, CPU bottlenecks |
| **Polars .profile()** | Query execution plan  | Text report     | Optimize Polars queries              |

---

## 1. memory-profiler {#memory-profiler}

### What It Does

-   **Profiles**: Memory (RAM) usage line-by-line
-   **Shows**: How much memory each line of code consumes
-   **Tracks**: Memory allocation, deallocation, and leaks

### How to Use

#### Method 1: Decorator (Recommended)

```python
from memory_profiler import profile

@profile
def my_function():
    df = pd.read_csv('large_file.csv')  # Shows memory increase
    df_filtered = df[df['amount'] > 100]  # Shows memory for copy
    return df_filtered
```

#### Method 2: Command Line

```bash
python -m memory_profiler pandas_profiling_demo.py
```

### What It Generates

**Output: Text Report in Terminal**

```
Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    47     180.2 MiB     180.2 MiB           1   @profile
    48                                           def perform_complex_joins():
    49     280.5 MiB     100.3 MiB           1       df_joined = df_orders.merge(...)
    50     420.8 MiB     140.3 MiB           1       df_full = df_joined.merge(...)
```

### How to Read It

-   **Mem usage**: Total memory at this point in execution
-   **Increment**: Memory added by THIS specific line
-   **Line Contents**: The actual code

### What You Learn

✅ Which lines consume most memory
✅ If memory is being released properly
✅ If you have memory leaks (memory keeps growing)
✅ Where to optimize memory usage

### Real Example from This Project

```bash
# Run pandas demo with memory profiling
python -m memory_profiler pandas_profiling_demo.py
```

**You'll see:**

-   Loading data: ~50 MB
-   First join: +100 MB (orders + customers)
-   Second join: +140 MB (adding products)
-   Peak memory: ~420 MB

**Insights:**

-   Joins are memory-intensive (creates copies)
-   Filtering after joins wastes memory
-   Should filter before joining when possible

---

## 2. ydata-profiling {#ydata-profiling}

### What It Does

-   **Profiles**: Your dataset statistics and quality
-   **Shows**: Distributions, correlations, missing values, outliers
-   **Automates**: Exploratory Data Analysis (EDA)

### How to Use

```python
from ydata_profiling import ProfileReport

df = pd.read_csv('data.csv')
profile = ProfileReport(df, title="My Dataset Profile")
profile.to_file("report.html")
```

### What It Generates

**Output: Interactive HTML Report** (`pandas_profile_report.html`)

**Sections in the Report:**

#### 1. Overview Tab

-   Number of variables (columns)
-   Number of observations (rows)
-   Missing cells percentage
-   Duplicate rows
-   Memory size

#### 2. Variables Tab

For EACH column:

-   **Numeric columns**:
    -   Min, max, mean, median, std
    -   Histogram showing distribution
    -   Outliers detected
    -   Missing values percentage
-   **Categorical columns**:
    -   Unique values count
    -   Most frequent values
    -   Bar chart of frequencies
-   **Date columns**:
    -   Date range
    -   Timeline plot
    -   Missing dates

#### 3. Interactions Tab

-   Correlation matrix (Pearson, Spearman)
-   Scatter plots between variables
-   Helps find relationships

#### 4. Correlations Tab

-   Pearson correlation (linear relationships)
-   Spearman correlation (monotonic relationships)
-   Cramér's V (categorical associations)

#### 5. Missing Values Tab

-   Matrix showing where values are missing
-   Patterns in missingness
-   Counts per variable

#### 6. Sample Tab

-   First 10 rows
-   Last 10 rows

### How to View It

```bash
# After running pandas_profiling_demo.py
open pandas_profile_report.html  # macOS
# or just double-click the HTML file
```

### What You Learn

✅ Data quality issues (missing values, duplicates)
✅ Outliers that need handling
✅ Distribution shapes (normal, skewed, bimodal)
✅ Correlations between variables
✅ Which columns have problems

### Real Example from This Project

```bash
# Generate the report
python pandas_profiling_demo.py

# Open in browser
open pandas_profile_report.html
```

**You'll discover:**

-   5% missing values in `amount` column (by design)
-   Distribution of orders across countries (USA dominates)
-   Correlation between product price and order amount
-   Customer segments distribution
-   Date range of orders (2020-2025)

---

## 3. py-spy {#py-spy}

### What It Does

-   **Profiles**: CPU time spent in each function
-   **Shows**: Where your program spends time (performance bottlenecks)
-   **Visualizes**: Call stacks as flame graphs

### How to Use

```bash
# Basic usage
py-spy record -o output.svg -- python your_script.py

# With native extensions (for Polars)
py-spy record -o output.svg --native -- python polars_demo.py

# Higher sampling rate (more detail)
py-spy record -o output.svg -r 500 -- python your_script.py
```

### What It Generates

**Output: SVG Flame Graph** (interactive, open in browser)

### How to Read Flame Graphs

**Visual Structure:**

```
[main]                                    ← Entry point (bottom)
  ├─[load_data]                          ← Called by main
  │   └─[read_parquet] ████              ← Wide = slow
  ├─[perform_joins] ████████████████     ← VERY WIDE = bottleneck!
  │   ├─[merge] ██████████               ← Most time in merge
  │   └─[validate] ██                    ← Less time
  └─[aggregations] ███                   ← Fast
```

**Key Concepts:**

-   **Width** = Time spent (wider = slower = bottleneck!)
-   **Height** = Call stack depth (how deep functions call each other)
-   **Color** = Random (just for visual separation)

**Interactive Features:**

-   Click on bars to zoom in
-   Hover to see function name and percentage
-   Search for specific functions (Ctrl+F)

### What You Learn

✅ Which functions are slow (wide bars)
✅ Where CPU time is spent
✅ Call patterns (who calls what)
✅ Python vs native code time

### Real Example from This Project

```bash
# Profile pandas (will take ~15 seconds)
py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py

# Profile polars with native code
py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

# Open the flame graphs
open pandas_profile.svg
open polars_profile.svg
```

**What You'll See:**

**Pandas Flame Graph:**

-   Wide bars in `merge()` function (slow joins)
-   Time spent in Python interpreter
-   Wide bars in `groupby()` operations
-   Overall execution spread across many functions

**Polars Flame Graph:**

-   Narrow bars (fast execution!)
-   Most time in native Rust code (if using --native)
-   Efficient parallel execution
-   Much smaller overall width

**Comparison:**

-   Pandas flame graph is ~150x wider than Polars
-   Polars shows more native code execution
-   Pandas shows more Python overhead

---

## 4. Polars .profile() {#polars-profile}

### What It Does

-   **Profiles**: Polars query execution plan
-   **Shows**: How Polars optimizes and executes your query
-   **Reveals**: Time spent in each operation

### How to Use

```python
import polars as pl

# Build lazy query
result_df, profile_info = (
    pl.scan_parquet('orders.parquet')
    .filter(pl.col('status') == 'completed')
    .join(pl.scan_parquet('customers.parquet'), on='customer_id')
    .group_by('country')
    .agg(pl.col('amount').sum())
    .profile()  # ← This profiles the query!
)

print(profile_info)  # Shows execution plan
```

### What It Generates

**Output: Text Report in Terminal**

```
╭────────────────────────┬────────┬────────────╮
│ node                   │ time   │ % of total │
├────────────────────────┼────────┼────────────┤
│ SCAN orders.parquet    │ 0.05s  │ 5%         │
│ FILTER                 │ 0.03s  │ 3%         │
│ SCAN customers.parquet │ 0.04s  │ 4%         │
│ JOIN                   │ 0.30s  │ 30%        │
│ GROUP BY               │ 0.25s  │ 25%        │
│ AGGREGATE              │ 0.20s  │ 20%        │
│ COLLECT                │ 0.13s  │ 13%        │
├────────────────────────┼────────┼────────────┤
│ TOTAL                  │ 1.00s  │ 100%       │
╰────────────────────────┴────────┴────────────╯
```

### What You Learn

✅ Query execution order (Polars optimizes!)
✅ Which operations are slow
✅ If query optimization is working
✅ Filter pushdown effectiveness

### Real Example from This Project

```bash
# Run polars demo (includes .profile() output)
python polars_profiling_demo.py
```

**You'll see:**

-   Query plan showing optimization
-   Time breakdown per operation
-   Proof that lazy evaluation works
-   Where the query bottleneck is (usually JOIN or COLLECT)

**Key Insight:**
Notice how FILTER runs BEFORE JOIN (filter pushdown optimization) - this is Polars being smart!

---

## When to Use Each Profiler {#when-to-use}

### Use memory-profiler when:

❓ "Why is my script using so much RAM?"
❓ "Where is the memory leak?"
❓ "Which function consumes most memory?"
❓ "Can I reduce memory usage?"

### Use ydata-profiling when:

❓ "What does my dataset look like?"
❓ "Are there data quality issues?"
❓ "What are the distributions?"
❓ "Which variables are correlated?"
❓ "Do I have outliers or missing values?"

### Use py-spy when:

❓ "Why is my script slow?"
❓ "Which function takes most CPU time?"
❓ "Where should I optimize first?"
❓ "Is the bottleneck in Python or native code?"

### Use Polars .profile() when:

❓ "Is my Polars query optimized?"
❓ "Where is the Polars query slow?"
❓ "Is lazy evaluation working?"
❓ "How does Polars execute my query?"

---

## Practical Examples {#practical-examples}

### Example 1: Finding Memory Leaks

**Problem:** Script memory keeps growing

**Solution:** Use memory-profiler

```bash
python -m memory_profiler pandas_profiling_demo.py
```

**Look for:**

-   Lines with large positive increments
-   Memory that never goes down
-   Accumulating objects in loops

**Fix:**

```python
# Bad: Memory leak
results = []
for chunk in chunks:
    results.append(process(chunk))  # Keeps growing!

# Good: Process and discard
for chunk in chunks:
    result = process(chunk)
    save_to_disk(result)  # Release memory
```

---

### Example 2: Understanding Your Data

**Problem:** New dataset, don't know what's in it

**Solution:** Use ydata-profiling

```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv('mystery_data.csv')
profile = ProfileReport(df, title="Dataset Analysis")
profile.to_file("report.html")
```

**Open report.html and discover:**

-   Missing values: 30% in column X (needs imputation)
-   Outliers: Values >1000 in column Y (need capping)
-   Correlations: Column A and B are 95% correlated (remove one)
-   Duplicates: 500 duplicate rows (need deduplication)

---

### Example 3: Speeding Up Slow Code

**Problem:** Script takes 10 minutes, need to speed up

**Solution:** Use py-spy

```bash
py-spy record -o profile.svg -- python slow_script.py
open profile.svg
```

**Analysis:**

-   See wide bar in `process_data()` function (70% of time)
-   Zoom into `process_data()`
-   See nested loop is the bottleneck
-   Optimize the loop → 10x speedup!

---

### Example 4: Optimizing Polars Queries

**Problem:** Polars query still slow

**Solution:** Use .profile()

```python
result, profile = (
    pl.scan_parquet('huge_file.parquet')
    .filter(...)  # Add filters
    .select(...)  # Select only needed columns
    .join(...)
    .profile()
)
print(profile)
```

**Analysis:**

-   See SCAN takes 60% of time
-   Add filter earlier to reduce data
-   Add select to load fewer columns
-   New profile shows 5x speedup!

---

## Quick Reference Commands

```bash
# 1. Memory profiling (RAM usage)
python -m memory_profiler pandas_profiling_demo.py

# 2. Data profiling (HTML report)
python pandas_profiling_demo.py
open pandas_profile_report.html

# 3. CPU profiling (flame graphs)
py-spy record -o pandas.svg -- python pandas_profiling_demo.py
py-spy record -o polars.svg --native -- python polars_profiling_demo.py
open pandas.svg

# 4. Query profiling (in code, automatic in polars_profiling_demo.py)
python polars_profiling_demo.py
```

---

## Summary Table

| Profiler              | What          | Output        | When               | Time to Run  |
| --------------------- | ------------- | ------------- | ------------------ | ------------ |
| **memory-profiler**   | RAM per line  | Terminal text | Memory issues      | +30% slower  |
| **ydata-profiling**   | Dataset stats | HTML report   | New dataset        | 2-3 minutes  |
| **py-spy**            | CPU time      | SVG graph     | Slow code          | +1-2% slower |
| **Polars .profile()** | Query plan    | Terminal text | Query optimization | Built-in     |

---

## Next Steps

1. **Start simple:** Run `python quick_benchmark.py` to see performance
2. **Add memory profiling:** Run with memory-profiler to see RAM usage
3. **Explore your data:** Check the HTML report from ydata-profiling
4. **Find bottlenecks:** Generate flame graphs with py-spy
5. **Optimize queries:** Use Polars .profile() for query tuning

---

**Remember:** Different profilers answer different questions. Use the right tool for your specific problem!
