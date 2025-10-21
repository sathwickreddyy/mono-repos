# py-spy Profiling Instructions

## What is py-spy?

py-spy is a sampling profiler for Python programs that can attach to running processes with minimal overhead. It generates flame graphs to visualize where your program spends time.

## Installation

Already included in requirements.txt:

```bash
pip install py-spy
```

## Basic Usage

### Profile Pandas Demo

```bash
# Generate flame graph (SVG)
py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py

# Generate flame graph with more samples (higher accuracy)
py-spy record -o pandas_profile.svg -r 100 -- python pandas_profiling_demo.py

# Generate speedscope format (interactive visualization)
py-spy record -o pandas_profile.speedscope.json -f speedscope -- python pandas_profiling_demo.py
```

### Profile Polars Demo

```bash
# Generate flame graph
py-spy record -o polars_profile.svg -- python polars_profiling_demo.py

# Profile with native mode (includes C extensions)
py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py
```

### Profile Comparison Demo

```bash
py-spy record -o comparison_profile.svg -- python comparison_demo.py
```

## Advanced Options

### Higher Sampling Rate

```bash
# Default is 100 samples/sec, increase for more detail
py-spy record -o profile.svg -r 500 -- python your_script.py
```

### Profile Running Process

```bash
# Find the process ID
ps aux | grep python

# Attach to running process
py-spy record -o profile.svg -p <PID> --duration 30
```

### Include Idle Time

```bash
# Show time spent waiting/sleeping
py-spy record -o profile.svg --idle -- python your_script.py
```

### Native Extensions

```bash
# Profile C/Rust extensions (useful for Polars)
py-spy record -o profile.svg --native -- python polars_profiling_demo.py
```

## Reading Flame Graphs

### Structure

-   **X-axis (width)**: Proportional to time spent in that function
-   **Y-axis (height)**: Call stack depth (bottom = entry point, top = leaf functions)
-   **Color**: Random colors for differentiation (not meaningful)

### Interpretation

1. **Wide bars**: Functions taking significant time

    - These are optimization targets
    - Look for unexpectedly wide bars

2. **Tall stacks**: Deep call chains

    - May indicate recursion or abstraction layers
    - Not necessarily bad, but can impact performance

3. **Flat tops**: CPU-bound code

    - Functions doing actual work
    - No further function calls

4. **Many thin bars**: Function call overhead
    - Consider inlining or reducing function calls

### What to Look For

#### In Pandas Scripts:

-   `merge`/`join` operations - Should be visible as wide bars
-   `groupby.agg` - Check aggregation time
-   `fillna`, `apply` - Row-wise operations are slow
-   `read_parquet` - I/O operations

#### In Polars Scripts:

-   Much of the work happens in Rust (may not be visible without --native)
-   `collect()` - Where lazy evaluation happens
-   `scan_*` operations - Should be fast (no actual reading)
-   Look for time in Python vs Rust code

#### Red Flags:

-   Unexpectedly wide bars in utility functions
-   Time spent in Python interpreter overhead
-   Excessive time in type checking or validation
-   Many small function calls (overhead)

## Comparison Analysis

### Run Both Profiles

```bash
py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py
py-spy record -o polars_profile.svg -- python polars_profiling_demo.py
```

### Compare:

1. **Total width**: Overall execution time
2. **Merge/join bars**: Pandas should be wider
3. **Python vs native code**: Polars spends more time in native code
4. **Stack depth**: Polars may have shallower stacks

## Flame Graph Tools

### View SVG Files

-   Open in any web browser
-   Click on bars to zoom in
-   Hover for function names and percentages
-   Use browser search (Ctrl+F) to find specific functions

### Alternative: speedscope

```bash
# Generate speedscope format
py-spy record -o profile.speedscope.json -f speedscope -- python your_script.py

# Visit https://www.speedscope.app/ and upload the JSON file
```

speedscope features:

-   Time-ordered view (left-to-right timeline)
-   Left-heavy view (traditional flame graph)
-   Sandwich view (caller/callee analysis)
-   Interactive zooming and filtering

## Troubleshooting

### Permission Denied

```bash
# On macOS/Linux, you may need sudo for attaching to processes
sudo py-spy record -o profile.svg -p <PID>
```

### Profile Shows Python Internals Only

```bash
# Add --native flag to see C/Rust extensions
py-spy record -o profile.svg --native -- python polars_profiling_demo.py
```

### Profile is Too Noisy

```bash
# Reduce sampling rate
py-spy record -o profile.svg -r 50 -- python your_script.py

# Or increase minimum function duration
py-spy record -o profile.svg --duration 60 -- python your_script.py
```

## Best Practices

1. **Run multiple times**: Results can vary, take averages
2. **Use realistic data**: Profile with production-like data sizes
3. **Profile end-to-end**: Don't just profile individual functions
4. **Compare before/after**: Profile before and after optimizations
5. **Use with memory-profiler**: py-spy shows time, memory-profiler shows memory
6. **Native mode for Polars**: Use --native to see Rust code performance

## Example Workflow

```bash
# 1. Generate sample data
python sample_data.py

# 2. Profile pandas implementation
py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py

# 3. Profile polars implementation (with native code)
py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py

# 4. Profile comparison script
py-spy record -o comparison_profile.svg -- python comparison_demo.py

# 5. Open SVG files in browser to analyze
open pandas_profile.svg
open polars_profile.svg
open comparison_profile.svg
```

## Quick Reference

| Command            | Description                          |
| ------------------ | ------------------------------------ |
| `-o <file>`        | Output file path                     |
| `-r <rate>`        | Sampling rate (samples/sec)          |
| `-f <format>`      | Output format (svg, speedscope, raw) |
| `--native`         | Profile native extensions            |
| `--idle`           | Include idle/wait time               |
| `-p <pid>`         | Attach to running process            |
| `--duration <sec>` | How long to profile                  |
| `--subprocesses`   | Profile child processes too          |

## Resources

-   py-spy GitHub: https://github.com/benfred/py-spy
-   Flame Graphs: http://www.brendangregg.com/flamegraphs.html
-   speedscope: https://www.speedscope.app/
