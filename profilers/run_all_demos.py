#!/usr/bin/env python3
"""
Master script to run all demos in sequence.
Perfect for a complete 30-minute learning session.
"""

import subprocess
import sys
import time

def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def run_script(script_name, description, estimated_time):
    """Run a Python script and track execution time."""
    print_section(f"Running: {description} (Est. {estimated_time} min)")
    
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        elapsed = time.time() - start
        print(f"\n✓ Completed in {elapsed:.1f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Failed with error code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return False

def main():
    """Run all demos in sequence."""
    print("\n" + "=" * 80)
    print(" " * 20 + "PANDAS & POLARS PROFILING")
    print(" " * 25 + "COMPLETE DEMO SUITE")
    print("=" * 80)
    
    total_start = time.time()
    
    demos = [
        ("sample_data.py", "Generate Sample Data (300K records)", 2),
        ("pandas_profiling_demo.py", "Pandas Profiling Demo", 8),
        ("polars_profiling_demo.py", "Polars Profiling Demo", 5),
        ("comparison_demo.py", "Performance Comparison", 5),
    ]
    
    results = []
    for script, description, est_time in demos:
        success = run_script(script, description, est_time)
        results.append((script, success))
        if not success:
            print(f"\nFailed to run {script}. Stopping.")
            break
    
    total_time = time.time() - total_start
    
    # Print summary
    print_section("EXECUTION SUMMARY")
    
    for script, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {script}")
    
    print(f"\n⏱  Total execution time: {total_time/60:.1f} minutes")
    
    if all(success for _, success in results):
        print("\n" + "=" * 80)
        print("✓ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📊 Generated outputs:")
        print("   - data/ directory with CSV and Parquet files")
        print("   - pandas_profile_report.html (comprehensive data report)")
        print("\n🔥 Next steps:")
        print("   1. Open pandas_profile_report.html in your browser")
        print("   2. Generate flame graphs:")
        print("      py-spy record -o pandas_profile.svg -- python pandas_profiling_demo.py")
        print("      py-spy record -o polars_profile.svg --native -- python polars_profiling_demo.py")
        print("   3. See py_spy_instructions.md for more profiling options")
        print("=" * 80)
    else:
        print("\n✗ Some demos failed. Check the output above for errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
