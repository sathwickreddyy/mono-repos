#!/usr/bin/env python3
"""
Display all available commands and their descriptions.
"""

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "PANDAS & POLARS PROFILING PROJECT")
    print(" " * 30 + "COMMAND REFERENCE")
    print("=" * 80)
    
    print_section("QUICK DEMOS (Pick One to Start)")
    
    demos = [
        ("quick_benchmark.py", "2-minute quick performance comparison", "⚡ RECOMMENDED FOR FIRST TIME"),
        ("run_all_demos.py", "Complete 30-minute tutorial with all demos", "🎓 COMPREHENSIVE LEARNING"),
        ("sample_data.py", "Generate 300K sample datasets", "📊 DATA GENERATION"),
        ("pandas_profiling_demo.py", "Pandas operations with memory profiling", "🐼 PANDAS DEEP DIVE"),
        ("polars_profiling_demo.py", "Polars with lazy execution profiling", "⚡ POLARS DEEP DIVE"),
        ("comparison_demo.py", "Side-by-side performance benchmarks", "📊 COMPARISON"),
    ]
    
    for script, description, tag in demos:
        print(f"\n  python {script:<30} # {description}")
        print(f"  {' ' * 38} {tag}")
    
    print_section("ADVANCED PROFILING")
    
    advanced = [
        ("python -m memory_profiler pandas_profiling_demo.py", "Line-by-line memory profiling"),
        ("py-spy record -o pandas.svg -- python pandas_profiling_demo.py", "Generate CPU flame graph"),
        ("py-spy record -o polars.svg --native -- python polars_profiling_demo.py", "Polars flame graph with native code"),
    ]
    
    for cmd, description in advanced:
        print(f"\n  {cmd}")
        print(f"  # {description}")
    
    print_section("UTILITY COMMANDS")
    
    utils = [
        ("python test_setup.py", "Verify all dependencies are installed"),
        ("pip list", "Show all installed packages"),
        ("ls -lh data/", "View generated data files"),
    ]
    
    for cmd, description in utils:
        print(f"\n  {cmd:<50} # {description}")
    
    print_section("VIEW OUTPUTS")
    
    outputs = [
        ("open pandas_profile_report.html", "View comprehensive data analysis report"),
        ("open pandas_profile.svg", "View pandas flame graph (after py-spy)"),
        ("open polars_profile.svg", "View polars flame graph (after py-spy)"),
    ]
    
    for cmd, description in outputs:
        print(f"\n  {cmd:<50} # {description}")
    
    print_section("DOCUMENTATION")
    
    docs = [
        ("cat README.md", "Comprehensive project documentation"),
        ("cat QUICKSTART.md", "Quick start guide"),
        ("cat PROJECT_SUMMARY.md", "Project completion summary"),
        ("cat py_spy_instructions.md", "Detailed py-spy profiling guide"),
    ]
    
    for cmd, description in docs:
        print(f"\n  {cmd:<50} # {description}")
    
    print_section("RECOMMENDED WORKFLOW")
    
    workflow = [
        "1. Run quick benchmark",
        "   python quick_benchmark.py",
        "",
        "2. Read the results and understand the performance difference",
        "",
        "3. Run full demo suite",
        "   python run_all_demos.py",
        "",
        "4. Explore the generated HTML report",
        "   open pandas_profile_report.html",
        "",
        "5. Generate flame graphs for deeper analysis",
        "   py-spy record -o pandas.svg -- python pandas_profiling_demo.py",
        "   py-spy record -o polars.svg --native -- python polars_profiling_demo.py",
        "",
        "6. View flame graphs",
        "   open pandas.svg",
        "   open polars.svg",
    ]
    
    for line in workflow:
        print(f"  {line}")
    
    print("\n" + "=" * 80)
    print(" " * 25 + "READY TO START!")
    print(" " * 15 + "Run: python quick_benchmark.py")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
