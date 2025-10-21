"""
Quick test to verify all dependencies are installed correctly.
"""

import sys

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    success = True
    
    packages = {
        'pandas': 'pandas',
        'polars': 'polars',
        'ydata_profiling': 'ydata-profiling',
        'memory_profiler': 'memory-profiler',
        'pyarrow': 'pyarrow',
        'matplotlib': 'matplotlib',
        'numpy': 'numpy'
    }
    
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            success = False
    
    # Check py-spy separately (it's a command-line tool)
    import subprocess
    try:
        result = subprocess.run(['py-spy', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print(f"✓ py-spy: {result.stdout.strip()}")
        else:
            print(f"✗ py-spy: command failed")
            success = False
    except Exception as e:
        print(f"✗ py-spy: {e}")
        success = False
    
    return success

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Dependency Check")
    print("=" * 60 + "\n")
    
    success = test_imports()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Run: python sample_data.py")
        print("2. Run: python pandas_profiling_demo.py")
        print("3. Run: python polars_profiling_demo.py")
        print("4. Run: python comparison_demo.py")
    else:
        print("✗ Some dependencies are missing!")
        print("Try: pip install -r requirements.txt")
        sys.exit(1)
    print("=" * 60)
