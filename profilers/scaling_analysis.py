#!/usr/bin/env python3
"""
Scaling Analysis Tool - Analyze memory and performance scaling characteristics.
Compare profiling results across different dataset sizes.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def parse_memory_profile(filepath: str) -> Dict[str, float]:
    """Parse memory profiler output and extract key metrics."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract peak memory
        memory_values = []
        for line in content.split('\n'):
            if 'MiB' in line:
                # Extract memory value
                match = re.search(r'(\d+\.?\d*)\s*MiB', line)
                if match:
                    memory_values.append(float(match.group(1)))
        
        if not memory_values:
            return {}
        
        return {
            'peak_memory': max(memory_values),
            'initial_memory': memory_values[0] if memory_values else 0,
            'final_memory': memory_values[-1] if memory_values else 0,
            'memory_growth': max(memory_values) - memory_values[0] if memory_values else 0
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return {}


def analyze_scaling(profiles: List[Tuple[int, Dict[str, float]]]) -> None:
    """Analyze scaling characteristics from multiple profiles."""
    print("\n" + "=" * 80)
    print(" " * 25 + "SCALING ANALYSIS REPORT")
    print("=" * 80)
    
    if len(profiles) < 2:
        print("\n⚠️  Need at least 2 profiles to analyze scaling.")
        print("Run profiling at different dataset sizes and try again.")
        return
    
    # Sort by dataset size
    profiles.sort(key=lambda x: x[0])
    
    print("\n📊 Memory Usage by Dataset Size")
    print("-" * 80)
    print(f"{'Dataset Size':<15} {'Peak Memory':<15} {'Memory/Row':<15} {'Growth':<15}")
    print("-" * 80)
    
    for size, metrics in profiles:
        if not metrics:
            continue
        peak = metrics.get('peak_memory', 0)
        memory_per_row = (peak / size) * 1024 if size > 0 else 0  # KB per row
        growth = metrics.get('memory_growth', 0)
        
        print(f"{size:>13,}  {peak:>12.1f} MB  {memory_per_row:>12.2f} KB  {growth:>12.1f} MB")
    
    # Analyze scaling factor
    print("\n" + "=" * 80)
    print("SCALING ANALYSIS")
    print("=" * 80)
    
    if len(profiles) >= 2:
        size1, metrics1 = profiles[0]
        size2, metrics2 = profiles[-1]
        
        if metrics1 and metrics2:
            data_ratio = size2 / size1
            memory_ratio = metrics2['peak_memory'] / metrics1['peak_memory']
            
            print(f"\n📈 Dataset Size Increase: {size1:,} → {size2:,} ({data_ratio:.2f}x)")
            print(f"📊 Memory Increase: {metrics1['peak_memory']:.1f} MB → {metrics2['peak_memory']:.1f} MB ({memory_ratio:.2f}x)")
            
            if abs(memory_ratio - data_ratio) < 0.2:
                print("✅ Scaling: LINEAR (excellent)")
            elif memory_ratio < data_ratio * 1.5:
                print("⚠️  Scaling: SLIGHTLY SUPER-LINEAR (acceptable)")
            else:
                print("❌ Scaling: SUPER-LINEAR (needs optimization)")
            
            # Predict for larger datasets
            print("\n" + "=" * 80)
            print("PREDICTIONS FOR LARGER DATASETS")
            print("=" * 80)
            
            # Calculate memory per row from latest profile
            memory_per_row = metrics2['peak_memory'] / size2
            
            for target_size in [1_000_000, 5_000_000, 10_000_000]:
                if target_size > size2:
                    predicted_memory = memory_per_row * target_size
                    print(f"\n{target_size:>10,} rows: ~{predicted_memory:>8.1f} MB ({predicted_memory/1024:.2f} GB)")
                    
                    if predicted_memory > 8192:  # > 8 GB
                        print("  ⚠️  WARNING: Exceeds 8GB. Consider:")
                        print("     - Using Polars for lower memory")
                        print("     - Streaming/chunked processing")
                        print("     - Data compression")


def compare_two_profiles(file1: str, file2: str) -> None:
    """Compare two memory profiles."""
    print("\n" + "=" * 80)
    print(" " * 25 + "PROFILE COMPARISON")
    print("=" * 80)
    
    metrics1 = parse_memory_profile(file1)
    metrics2 = parse_memory_profile(file2)
    
    if not metrics1 or not metrics2:
        print("\n❌ Error: Could not parse one or both profile files")
        return
    
    print(f"\nProfile 1: {file1}")
    print(f"  Peak Memory: {metrics1['peak_memory']:.1f} MB")
    print(f"  Memory Growth: {metrics1['memory_growth']:.1f} MB")
    
    print(f"\nProfile 2: {file2}")
    print(f"  Peak Memory: {metrics2['peak_memory']:.1f} MB")
    print(f"  Memory Growth: {metrics2['memory_growth']:.1f} MB")
    
    print("\n" + "-" * 80)
    print("COMPARISON")
    print("-" * 80)
    
    peak_diff = metrics2['peak_memory'] - metrics1['peak_memory']
    peak_ratio = metrics2['peak_memory'] / metrics1['peak_memory']
    
    print(f"Peak Memory Difference: {peak_diff:+.1f} MB ({peak_ratio:.2f}x)")
    
    if peak_ratio > 1.1:
        print("⚠️  Profile 2 uses significantly more memory")
    elif peak_ratio < 0.9:
        print("✅ Profile 2 uses less memory (optimization successful!)")
    else:
        print("➡️  Similar memory usage")


def interactive_analysis():
    """Interactive mode for scaling analysis."""
    print("\n" + "=" * 80)
    print(" " * 20 + "SCALING ANALYSIS TOOL")
    print("=" * 80)
    
    print("\nThis tool analyzes memory scaling characteristics from profiler outputs.")
    print("\nOptions:")
    print("1. Analyze scaling across multiple dataset sizes")
    print("2. Compare two profiles")
    print("3. Quick analysis of current directory")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\nEnter profile information (press Enter with empty input to finish):")
        profiles = []
        
        while True:
            size_input = input("\nDataset size (e.g., 300000): ").strip()
            if not size_input:
                break
            
            filepath = input("Memory profile file path: ").strip()
            
            try:
                size = int(size_input.replace(',', ''))
                metrics = parse_memory_profile(filepath)
                if metrics:
                    profiles.append((size, metrics))
                else:
                    print("⚠️  Could not parse profile file")
            except ValueError:
                print("⚠️  Invalid dataset size")
        
        if profiles:
            analyze_scaling(profiles)
        else:
            print("\n❌ No valid profiles provided")
    
    elif choice == '2':
        file1 = input("\nFirst profile file: ").strip()
        file2 = input("Second profile file: ").strip()
        compare_two_profiles(file1, file2)
    
    elif choice == '3':
        # Look for memory profile files in current directory
        profile_files = sorted(Path('.').glob('*memory*.txt'))
        
        if not profile_files:
            print("\n⚠️  No *memory*.txt files found in current directory")
            return
        
        print(f"\nFound {len(profile_files)} profile file(s):")
        for i, f in enumerate(profile_files, 1):
            print(f"{i}. {f.name}")
        
        print("\nAnalyzing all profiles...")
        
        # Try to extract dataset size from filename
        profiles = []
        for f in profile_files:
            # Look for numbers in filename (e.g., profile_300k_memory.txt)
            match = re.search(r'(\d+)k', f.name, re.IGNORECASE)
            if match:
                size = int(match.group(1)) * 1000
            else:
                match = re.search(r'(\d+)m', f.name, re.IGNORECASE)
                if match:
                    size = int(match.group(1)) * 1_000_000
                else:
                    size = len(profiles) * 100000  # Default estimation
            
            metrics = parse_memory_profile(str(f))
            if metrics:
                profiles.append((size, metrics))
        
        if profiles:
            analyze_scaling(profiles)


def main():
    """Main function."""
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_analysis()
    elif len(sys.argv) == 3 and sys.argv[1] == '--compare':
        # Command line comparison mode
        compare_two_profiles(sys.argv[2], sys.argv[3])
    else:
        print("Usage:")
        print("  python scaling_analysis.py                    # Interactive mode")
        print("  python scaling_analysis.py --compare file1 file2  # Compare two profiles")


if __name__ == "__main__":
    main()
