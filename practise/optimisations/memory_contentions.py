import threading
import time

class SimpleMemoryContentionDemo:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

    def unsafe_increment(self):
        """Increment counter without protection - causes race conditions"""
        for i in range(10000):
            # Step 1: Thread reads current counter value
            temp = self.counter  # e.g., Thread A reads 0
            
            # Step 2: GIL releases during sleep, other threads get to run
            time.sleep(0.0001)   # Thread B also reads 0, Thread C reads 0, etc.
            
            # Step 3: When this thread resumes, it writes back old_value + 1
            self.counter = temp + 1  # All threads write 0 + 1 = 1
            # Result: Instead of 5 increments, we get just 1!

    def safe_increment(self):
        """Increment counter with lock protection - thread safe"""
        for i in range(10000):
            with self.lock:
                temp = self.counter
                time.sleep(0.0001)  # Same delay but protected
                self.counter = temp + 1

    def run_demo(self):
        print("Simple Memory Contention Demo")
        print("=" * 40)
        
        # Test 1: Without locks (unsafe)
        print("\n1. WITHOUT LOCKS (Race Condition):")
        self.counter = 0
        threads = []
        
        # Create 5 threads
        for i in range(5):
            t = threading.Thread(target=self.unsafe_increment)
            threads.append(t)
            t.start()
        
        # Wait for all threads to finish
        for t in threads:
            t.join()
        
        expected = 5 * 10000  # 5 threads × 10000 increments each
        print(f"Expected: {expected}")
        print(f"Actual:   {self.counter}")
        print(f"Lost:     {expected - self.counter} increments!")
        
        # Test 2: With locks (safe)
        print("\n2. WITH LOCKS (Thread Safe):")
        self.counter = 0
        threads = []
        
        # Same 5 threads but with locks
        for i in range(5):
            t = threading.Thread(target=self.safe_increment)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print(f"Expected: {expected}")
        print(f"Actual:   {self.counter}")
        print(f"Lost:     {expected - self.counter} increments")
        
        print("\n" + "=" * 40)
        print("What's happening with GIL:")
        print("1. Thread A reads counter = 0")
        print("2. time.sleep() releases GIL")
        print("3. Thread B runs, reads counter = 0") 
        print("4. Thread C runs, reads counter = 0")
        print("5. All threads write back 0 + 1 = 1")
        print("6. Result: 5 threads but counter = 1 (not 5!)")
        print("\nThis is why we lose increments - multiple")
        print("threads see the same old value!")

def demonstrate_gil_switching():
    """Show step-by-step what happens with GIL switching"""
    print("\n" + "=" * 50)
    print("GIL Thread Switching Visualization")
    print("=" * 50)
    
    counter = 0
    
    print(f"Initial counter: {counter}")
    print("\nStep-by-step execution:")
    print("Thread A: reads counter =", counter, "→ temp = 0")
    print("Thread A: sleeps (GIL released)")
    print("Thread B: reads counter =", counter, "→ temp = 0") 
    print("Thread B: sleeps (GIL released)")
    print("Thread C: reads counter =", counter, "→ temp = 0")
    print("Thread C: sleeps (GIL released)")
    print("...")
    print("Thread A: wakes up, writes temp + 1 =", 0 + 1)
    counter = 1
    print("Thread B: wakes up, writes temp + 1 =", 0 + 1)  # Still writes 1!
    print("Thread C: wakes up, writes temp + 1 =", 0 + 1)  # Still writes 1!
    print(f"\nFinal counter: {counter} (should be 3, but it's 1)")
    print("Two increments were LOST!")

if __name__ == "__main__":
    demo = SimpleMemoryContentionDemo()
    demo.run_demo()
    demonstrate_gil_switching()
        
            
