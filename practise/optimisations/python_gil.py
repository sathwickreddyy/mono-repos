import time
import threading
from multiprocessing import Process, cpu_count

# CPU-intensive function that does heavy computation
def cpu_intensive_task(n):
    """Simulate CPU-bound work by calculating sum of squares"""
    total = 0
    for i in range(n):
        total += i * i
    return total

# Function to run tasks sequentially (baseline)
def run_sequential(iterations):
    print("\n=== SEQUENTIAL EXECUTION (Baseline) ===")
    start_time = time.time()
    
    for _ in range(14):
        cpu_intensive_task(iterations)

    end_time = time.time()
    print(f"Sequential time: {end_time - start_time:.4f} seconds")
    return end_time - start_time

# Function to run tasks with threading
def run_with_threading(iterations):
    print("\n=== MULTITHREADING (GIL Limited) ===")
    start_time = time.time()
    
    threads = []
    for _ in range(14):
        thread = threading.Thread(target=cpu_intensive_task, args=(iterations,))
        threads.append(thread)
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Threading time: {end_time - start_time:.4f} seconds")
    print(f"⚠️  Notice: Threading is SLOWER or equal to sequential due to GIL overhead!")
    return end_time - start_time

# Function to run tasks with multiprocessing
def run_with_multiprocessing(iterations):
    print("\n=== MULTIPROCESSING (True Parallelism) ===")
    start_time = time.time()
    
    processes = []
    for _ in range(14):
        process = Process(target=cpu_intensive_task, args=(iterations,))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    end_time = time.time()
    print(f"Multiprocessing time: {end_time - start_time:.4f} seconds")
    print(f"✅ Multiprocessing achieves true parallelism by bypassing GIL!")
    return end_time - start_time

if __name__ == "__main__":
    # Use a large number to make the task CPU-intensive
    # Adjust this based on your Mac's performance (higher = more strain)
    ITERATIONS = 50_000_000  # 500 million iterations
    
    print(f"CPU Cores available: {cpu_count()}")
    print(f"Running CPU-intensive task with {ITERATIONS:,} iterations per task")
    print("=" * 60)
    
    # Run all three approaches
    seq_time = run_sequential(ITERATIONS)
    thread_time = run_with_threading(ITERATIONS)
    process_time = run_with_multiprocessing(ITERATIONS)
    
    # Summary
    print("\n" + "=" * 60)
    print("=== PERFORMANCE SUMMARY ===")
    print(f"Sequential:       {seq_time:.4f} seconds (baseline)")
    print(f"Threading:        {thread_time:.4f} seconds ({thread_time/seq_time:.2f}x)")
    print(f"Multiprocessing:  {process_time:.4f} seconds ({process_time/seq_time:.2f}x)")
    print("\n🔍 Key Observation:")
    print("   - Threading: Same or SLOWER than sequential (GIL prevents parallelism)")
    print("   - Multiprocessing: ~50% faster (true parallelism on 2+ cores)")
