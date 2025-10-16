# Quick Start Guide

## 🚀 5-Minute Setup

```bash
# 1. Navigate to project directory
cd /Users/sathwick/IdeaProjects/mono-repos/profilers

# 2. Activate virtual environment
source venv/bin/activate  # Already created and ready!

# 3. Verify installation (optional)
python test_setup.py

# 4. Generate sample data
python sample_data.py

# 5. Run all demos
python run_all_demos.py
```

## ✅ What's Already Done

-   ✓ Virtual environment created (`venv/`)
-   ✓ All dependencies installed
-   ✓ Sample data generated (360K rows)
-   ✓ Ready to run!

## 📁 Project Files

### Core Scripts

1. **sample_data.py** - Generates realistic e-commerce data
    - 300K orders
    - 50K customers
    - 10K products
2. **pandas_profiling_demo.py** - Pandas operations with memory profiling
    - Complex 3-way joins
    - Groupby aggregations
    - ydata-profiling HTML report
3. **polars_profiling_demo.py** - Polars with lazy execution
    - Query optimization
    - Lazy vs eager comparison
    - Streaming execution
4. **comparison_demo.py** - Side-by-side performance benchmarks
    - Loading speed
    - Join performance
    - Aggregation speed
    - Memory usage

### Helper Scripts

-   **test_setup.py** - Verify dependencies
-   **run_all_demos.py** - Run all demos in sequence

### Documentation

-   **README.md** - Complete project documentation
-   **py_spy_instructions.md** - Flame graph profiling guide
-   **QUICKSTART.md** - This file!

## 🎯 Learning Path (30 minutes)

### Part 1: Data Generation (2 min)

```bash
python sample_data.py
```

**Learn**: How to generate realistic datasets with missing values

### Part 2: Pandas Profiling (8 min)

```bash
python pandas_profiling_demo.py
```

**Learn**:

-   Memory profiling with @profile decorator
-   Complex joins and aggregations
-   ydata-profiling reports

### Part 3: Polars Profiling (5 min)

```bash
python polars_profiling_demo.py
```

**Learn**:

-   Lazy evaluation and query optimization
-   .profile() method for query analysis
-   Streaming execution

### Part 4: Performance Comparison (5 min)

```bash
python comparison_demo.py
```

**Learn**:

-   Performance differences
-   When to use each library
-   Memory efficiency

### Part 5: Flame Graphs (10 min)

```bash
# Generate flame graphs
py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py
py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

# Open in browser
open pandas_profile.svg
open polars_profile.svg
```

**Learn**:

-   CPU profiling visualization
-   Identifying bottlenecks
-   Comparing implementations

## 📊 Expected Results

### Performance (300K records)

-   **Pandas**: 5-7 seconds total
-   **Polars**: 1.5-2.5 seconds total
-   **Speedup**: 3-4x faster with Polars

### Memory Usage

-   **Pandas**: 200-300 MB peak
-   **Polars**: 150-200 MB peak
-   **Efficiency**: 1.5x more efficient with Polars

## 🔥 Pro Tips

### Run with Memory Profiling

```bash
python -m memory_profiler pandas_profiling_demo.py
```

### Run All at Once

```bash
python run_all_demos.py
```

### Generate Different Data Sizes

Edit `sample_data.py` and change:

```python
def generate_orders(n_orders=100_000, ...)  # Smaller dataset
def generate_orders(n_orders=500_000, ...)  # Larger dataset
```

### Profile Specific Functions

Add `@profile` decorator to any function in your code!

## 📈 Generated Outputs

After running demos, you'll have:

-   `data/` - CSV and Parquet files
-   `pandas_profile_report.html` - Comprehensive data analysis
-   `*.svg` - Flame graphs (if you run py-spy)

## 🆘 Troubleshooting

### Memory Error

```bash
# Reduce dataset size in sample_data.py
n_orders=100_000  # Instead of 300_000
```

### ydata-profiling Too Slow

```python
# In pandas_profiling_demo.py, use minimal=True
profile = ProfileReport(df, minimal=True)
```

### Permission Denied (py-spy)

```bash
# On macOS, may need sudo
sudo py-spy record -o profile.svg -- python script.py
```

## 🎓 Next Steps

1. **Explore the code** - Read inline comments
2. **Modify operations** - Try different joins and filters
3. **Profile your data** - Replace sample data with your own
4. **Optimize** - Use flame graphs to find bottlenecks
5. **Share** - Compare results with others

## 📚 Key Takeaways

**Use Pandas when**:

-   Dataset < 100K rows
-   Need scikit-learn integration
-   Familiar with the API

**Use Polars when**:

-   Dataset > 100K rows
-   Performance is critical
-   Working with large datasets
-   Need streaming capabilities

## 🔗 Resources

-   See `README.md` for detailed documentation
-   See `py_spy_instructions.md` for profiling guide
-   All scripts have extensive inline comments

---

**Ready to start? Run:** `python run_all_demos.py`
