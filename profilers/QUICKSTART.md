# Quick Start Guide - Scaling Analysis with Profilers# Quick Start Guide



## 🚀 5-Minute Setup## 🚀 5-Minute Setup



```bash```bash

# 1. Navigate to project directory# 1. Navigate to project directory

cd /Users/sathwick/IdeaProjects/mono-repos/profilerscd /Users/sathwick/IdeaProjects/mono-repos/profilers



# 2. Activate virtual environment  # 2. Activate virtual environment

source venv/bin/activate  # Already created!source venv/bin/activate  # Already created and ready!



# 3. Install dependencies (updated, streamlined)# 3. Verify installation (optional)

pip install -r requirements.txtpython test_setup.py



# 4. Generate sample data# 4. Generate sample data

python sample_data.pypython sample_data.py



# 5. Run with profiling# 5. Run all demos

python -m memory_profiler pandas_profiling_demo.pypython run_all_demos.py

``````



## ✅ What's Ready## ✅ What's Already Done



- ✓ Virtual environment created (`venv/`)-   ✓ Virtual environment created (`venv/`)

- ✓ Dependencies streamlined (memory-profiler + py-spy focus)-   ✓ All dependencies installed

- ✓ Sample data generated (360K rows)-   ✓ Sample data generated (360K rows)

- ✓ Ready for scaling analysis-   ✓ Ready to run!



## 📊 Two Essential Profilers## 📁 Project Files



### 1. memory-profiler (RAM Usage)### Core Scripts

**What it shows:** Line-by-line memory consumption

1. **sample_data.py** - Generates realistic e-commerce data

**Use when:**    - 300K orders

- Finding memory leaks    - 50K customers

- Optimizing RAM usage    - 10K products

- Predicting memory needs for larger datasets2. **pandas_profiling_demo.py** - Pandas operations with memory profiling

    - Complex 3-way joins

**How to run:**    - Groupby aggregations

```bash    - ydata-profiling HTML report

python -m memory_profiler pandas_profiling_demo.py3. **polars_profiling_demo.py** - Polars with lazy execution

python -m memory_profiler polars_profiling_demo.py    - Query optimization

python -m memory_profiler comparison_demo.py    - Lazy vs eager comparison

```    - Streaming execution

4. **comparison_demo.py** - Side-by-side performance benchmarks

**What you get:**    - Loading speed

```    - Join performance

Line #    Mem usage    Increment  Line Contents    - Aggregation speed

================================================    - Memory usage

    49     280.5 MiB   100.3 MiB     df_joined = df_orders.merge(...)

    50     420.8 MiB   140.3 MiB     df_full = df_joined.merge(...)### Helper Scripts

```

-   **test_setup.py** - Verify dependencies

### 2. py-spy (CPU Time)-   **run_all_demos.py** - Run all demos in sequence

**What it shows:** Interactive flame graph of CPU usage

### Documentation

**Use when:**

- Finding performance bottlenecks-   **README.md** - Complete project documentation

- Identifying slow functions-   **py_spy_instructions.md** - Flame graph profiling guide

- Comparing implementations-   **QUICKSTART.md** - This file!



**How to run:**## 🎯 Learning Path (30 minutes)

```bash

py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py### Part 1: Data Generation (2 min)

py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

open pandas_profile.svg```bash

```python sample_data.py

```

**What you get:** SVG flame graph where width = time spent

**Learn**: How to generate realistic datasets with missing values

## 🎯 Scaling Analysis Workflow (30 minutes)

### Part 2: Pandas Profiling (8 min)

### Part 1: Profile at Current Scale (10 min)

```bash```bash

# Generate 300K rowspython pandas_profiling_demo.py

python sample_data.py```



# Memory profiling**Learn**:

python -m memory_profiler comparison_demo.py > profile_300k_memory.txt

-   Memory profiling with @profile decorator

# CPU profiling-   Complex joins and aggregations

py-spy record -o profile_300k.svg -- python comparison_demo.py-   ydata-profiling reports

```

### Part 3: Polars Profiling (5 min)

**Learn:** Baseline memory and CPU usage

```bash

### Part 2: Profile at Larger Scale (10 min)python polars_profiling_demo.py

```bash```

# Edit sample_data.py: change n_orders=1_000_000

python sample_data.py**Learn**:



# Memory profiling-   Lazy evaluation and query optimization

python -m memory_profiler comparison_demo.py > profile_1m_memory.txt-   .profile() method for query analysis

-   Streaming execution

# CPU profiling

py-spy record -o profile_1m.svg -- python comparison_demo.py### Part 4: Performance Comparison (5 min)

```

```bash

**Learn:** How memory and time scale with datapython comparison_demo.py

```

### Part 3: Analyze Scaling (10 min)

```bash**Learn**:

# Compare memory profiles

python scaling_analysis.py --compare profile_300k_memory.txt profile_1m_memory.txt-   Performance differences

-   When to use each library

# Compare flame graphs-   Memory efficiency

open profile_300k.svg

open profile_1m.svg### Part 5: Flame Graphs (10 min)

```

```bash

**Learn:**# Generate flame graphs

- Is scaling linear?py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py

- Where are the bottlenecks?py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

- Which library scales better?

# Open in browser

## 📈 Expected Resultsopen pandas_profile.svg

open polars_profile.svg

### Memory Scaling (300K records)```

- **Pandas**: 280 MB (0.93 KB/row)

- **Polars**: 180 MB (0.60 KB/row)**Learn**:

- **Winner**: Polars (35% less memory)

-   CPU profiling visualization

### CPU Time (300K records)-   Identifying bottlenecks

- **Pandas**: 5-7 seconds-   Comparing implementations

- **Polars**: 1.5-2.5 seconds

- **Speedup**: 3-4x faster with Polars## 📊 Expected Results



## 🔥 Pro Tips### Performance (300K records)



### Memory Profiling-   **Pandas**: 5-7 seconds total

```bash-   **Polars**: 1.5-2.5 seconds total

# Save output for analysis-   **Speedup**: 3-4x faster with Polars

python -m memory_profiler script.py > memory_report.txt

### Memory Usage

# Extract peak memory

cat memory_report.txt | grep "MiB" | sort -k2 -n | tail -1-   **Pandas**: 200-300 MB peak

```-   **Polars**: 150-200 MB peak

-   **Efficiency**: 1.5x more efficient with Polars

### CPU Profiling

```bash## 🔥 Pro Tips

# Higher sampling rate (more detail)

py-spy record -o profile.svg -r 500 -- python script.py### Run with Memory Profiling



# Include native code (for Polars/NumPy)```bash

py-spy record -o profile.svg --native -- python script.pypython -m memory_profiler pandas_profiling_demo.py

```

# Profile specific duration

py-spy record -o profile.svg --duration 30 -- python script.py### Run All at Once

```

```bash

## 🎓 Key Insights for Scalingpython run_all_demos.py

```

### From memory-profiler:

1. **Peak memory usage** → Predict RAM needs### Generate Different Data Sizes

2. **Memory per row** → Calculate for larger datasets

3. **Memory leaks** → Lines where memory doesn't dropEdit `sample_data.py` and change:

4. **Optimization targets** → Largest memory increments

```python

### From py-spy flame graphs:def generate_orders(n_orders=100_000, ...)  # Smaller dataset

1. **Wide bars** → Functions to optimize firstdef generate_orders(n_orders=500_000, ...)  # Larger dataset

2. **Comparison** → pandas vs polars side-by-side```

3. **Parallelization** → Single bar vs many bars

4. **Native code** → Time in Python vs C/Rust### Profile Specific Functions



## 📊 Scaling PredictionsAdd `@profile` decorator to any function in your code!



```python## 📈 Generated Outputs

# If 300K rows = 200 MB:

memory_per_row = 200 MB / 300_000 = 0.67 KB/rowAfter running demos, you'll have:



# Predict for 10M rows:-   `data/` - CSV and Parquet files

memory_10m = 0.67 KB/row * 10_000_000 = 6.7 GB-   `pandas_profile_report.html` - Comprehensive data analysis

-   `*.svg` - Flame graphs (if you run py-spy)

# Decision: Will fit in 8GB RAM? ✅

```## 🆘 Troubleshooting



## 🆘 Troubleshooting### Memory Error



### Memory Profiler Not Working```bash

```bash# Reduce dataset size in sample_data.py

# Make sure to use -m flagn_orders=100_000  # Instead of 300_000

python -m memory_profiler script.py```



# Not this:### ydata-profiling Too Slow

python script.py  # Won't show profiling

``````python

# In pandas_profiling_demo.py, use minimal=True

### py-spy Permission Deniedprofile = ProfileReport(df, minimal=True)

```bash```

# On macOS, might need sudo

sudo py-spy record -o profile.svg -- python script.py### Permission Denied (py-spy)

```

```bash

### Out of Memory# On macOS, may need sudo

```bashsudo py-spy record -o profile.svg -- python script.py

# Reduce dataset size in sample_data.py```

n_orders = 100_000  # Instead of 300_000

```## 🎓 Next Steps



## 📚 Next Steps1. **Explore the code** - Read inline comments

2. **Modify operations** - Try different joins and filters

1. **Understand**: Run `python quick_benchmark.py` to see performance3. **Profile your data** - Replace sample data with your own

2. **Profile Memory**: Run with memory-profiler4. **Optimize** - Use flame graphs to find bottlenecks

3. **Profile CPU**: Generate flame graphs5. **Share** - Compare results with others

4. **Analyze Scaling**: Use `scaling_analysis.py`

5. **Optimize**: Apply findings to your code## 📚 Key Takeaways



## 🔗 Key Files**Use Pandas when**:



- `README.md` - Complete scaling analysis guide-   Dataset < 100K rows

- `scaling_analysis.py` - Analyze profiling results-   Need scikit-learn integration

- `py_spy_instructions.md` - Detailed flame graph guide-   Familiar with the API

- `PROFILERS_GUIDE.md` - Comprehensive profiler documentation

**Use Polars when**:

---

-   Dataset > 100K rows

**Focus: Memory + CPU profiling for scaling analysis** 🚀-   Performance is critical

-   Working with large datasets
-   Need streaming capabilities

## 🔗 Resources

-   See `README.md` for detailed documentation
-   See `py_spy_instructions.md` for profiling guide
-   All scripts have extensive inline comments

---

**Ready to start? Run:** `python run_all_demos.py`
