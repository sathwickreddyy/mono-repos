# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pandas as pd
import time
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global thread pool for I/O operations (CSV reading)
thread_pool = ThreadPoolExecutor(max_workers=8)

# Data handling module
class DataHandler:
    @staticmethod
    def create_sample_csv():
        """Create sample CSV files for testing"""
        logger.debug("Creating sample CSV file with 1000 rows")
        df = pd.DataFrame({
            'id': range(1000),
            'value': range(1000, 2000),
            'category': ['A', 'B', 'C', 'D'] * 250
        })
        df.to_csv('sample_data.csv', index=False)
        logger.debug(f"Sample CSV created successfully with columns: {list(df.columns)}")
    
    @staticmethod
    def load_data() -> pd.DataFrame:
        """Load data from CSV file"""
        logger.debug("Loading data from sample_data.csv")
        df = pd.read_csv('sample_data.csv')
        logger.debug(f"Data loaded successfully - Shape: {df.shape}, Columns: {list(df.columns)}")
        logger.debug(f"Sample data preview: {df.head(2).to_dict('records')}")
        return df
    
    @staticmethod
    def prepare_data_for_processing(df: pd.DataFrame) -> Dict[str, Dict]:
        """Prepare data for processing in a multiprocessing-friendly format"""
        logger.debug(f"Preparing data for processing - Original DataFrame shape: {df.shape}")
        df2 = df.copy()
        df2['value'] = df2['value'] * 1.5
        logger.debug(f"Created second DataFrame with modified values - Shape: {df2.shape}")
        
        # Convert to dict for multiprocessing (DataFrames can cause pickle issues)
        data_dict = {
            'df1': df.to_dict('list'),
            'df2': df2.to_dict('list')
        }
        logger.debug("Successfully converted DataFrames to dictionaries for multiprocessing")
        return data_dict

# Processing module
class ScenarioProcessor:
    @staticmethod
    def process_scenario(args: tuple) -> Dict[str, Any]:
        """
        Process a single scenario combination with Pandas operations
        This simulates complex data transformations with joins
        """
        scenario_id, data_dict = args
        logger.debug(f"Processing scenario {scenario_id} - Starting data conversion from dict to DataFrame")
        
        # Convert dict back to DataFrame (needed for multiprocessing)
        df1 = pd.DataFrame(data_dict['df1'])
        df2 = pd.DataFrame(data_dict['df2'])
        logger.debug(f"Scenario {scenario_id} - DataFrames created: df1 shape={df1.shape}, df2 shape={df2.shape}")
        logger.debug(f"Scenario {scenario_id} - df1 columns: {list(df1.columns)}, df2 columns: {list(df2.columns)}")
        
        # Simulate complex operations: multiple joins, aggregations
        logger.debug(f"Scenario {scenario_id} - Performing inner merge on 'id' column")
        result = df1.merge(df2, on='id', how='inner')
        logger.debug(f"Scenario {scenario_id} - Merge completed, result shape: {result.shape}")
        logger.debug(f"Scenario {scenario_id} - Merged columns: {list(result.columns)}")
        
        # Check if 'category' column exists in the result DataFrame
        if 'category' not in result.columns:
            logger.warning(f"Scenario {scenario_id} - 'category' column not found in merged result")
            # If not, we need to make sure it gets carried through the merge
            if 'category_x' in result.columns:
                result['category'] = result['category_x']
                logger.debug(f"Scenario {scenario_id} - Using 'category_x' as 'category' column")
            elif 'category_y' in result.columns:
                result['category'] = result['category_y']
                logger.debug(f"Scenario {scenario_id} - Using 'category_y' as 'category' column")
            else:
                # If we can't find it at all, add a default category to prevent error
                result['category'] = 'default'
                logger.warning(f"Scenario {scenario_id} - No category columns found, using default value")
        else:
            logger.debug(f"Scenario {scenario_id} - 'category' column found in merged result")
        
        # Now we can safely group by category
        logger.debug(f"Scenario {scenario_id} - Performing groupby operation on 'category'")
        unique_categories = result['category'].unique()
        logger.debug(f"Scenario {scenario_id} - Found categories: {list(unique_categories)}")
        
        result = result.groupby('category').agg({
            'value_x': 'sum',
            'value_y': 'mean'
        }).reset_index()
        logger.debug(f"Scenario {scenario_id} - Groupby completed, result shape: {result.shape}")
        
        # Simulate additional computation
        result['computed'] = result['value_x'] * result['value_y'] / 100
        logger.debug(f"Scenario {scenario_id} - Computed column added")
        
        # Calculate final metrics
        final_sum = result['computed'].sum()
        logger.debug(f"Scenario {scenario_id} - Processing completed: {len(result)} rows, sum_computed={final_sum:.2f}")
        
        time.sleep(0.1)  # Simulate processing time
        
        return {
            'scenario_id': scenario_id,
            'result_rows': len(result),
            'sum_computed': final_sum
        }
    
    @staticmethod
    def run_scenarios(data_dict: Dict, num_scenarios: int = 16) -> List[Dict]:
        """Process multiple scenarios using a process pool"""
        logger.debug(f"Preparing to run {num_scenarios} scenarios using ProcessPoolExecutor")
        scenarios = [(i, data_dict) for i in range(num_scenarios)]
        logger.debug(f"Created {len(scenarios)} scenario tuples for processing")
        
        with ProcessPoolExecutor(max_workers=4) as process_pool:
            logger.debug("ProcessPoolExecutor started with 4 workers")
            results = list(process_pool.map(ScenarioProcessor.process_scenario, scenarios))
            logger.debug(f"ProcessPoolExecutor completed successfully. Processed {len(results)} scenarios")
            return results

# Worker module
class Worker:
    @staticmethod
    def thread_worker(request_id: int) -> Dict:
        """
        I/O-bound task: Read CSV data using Pandas
        Then spawn ProcessPoolExecutor for CPU-bound scenario processing
        """
        start_time = time.time()
        logger.debug(f"Thread {request_id}: Starting worker thread for request processing")
        
        # Step 1: I/O-bound operation - read CSV with Pandas
        logger.debug(f"Thread {request_id}: Reading CSV data")
        df = DataHandler.load_data()
        logger.debug(f"Thread {request_id}: CSV data loaded, DataFrame shape: {df.shape}")
        
        # Prepare data for scenarios
        logger.debug(f"Thread {request_id}: Preparing data for multiprocessing scenarios")
        data_dict = DataHandler.prepare_data_for_processing(df)
        logger.debug(f"Thread {request_id}: Data preparation completed")
        
        # Step 2: CPU-bound operation - spawn ProcessPoolExecutor
        logger.debug(f"Thread {request_id}: Starting ProcessPoolExecutor with 4 workers")
        results = ScenarioProcessor.run_scenarios(data_dict)
        logger.debug(f"Thread {request_id}: ProcessPoolExecutor completed, processed {len(results)} scenarios")
        
        execution_time = time.time() - start_time
        logger.debug(f"Thread {request_id}: Worker thread completed in {execution_time:.2f} seconds")
        
        return {
            'request_id': request_id,
            'scenarios_processed': len(results),
            'execution_time': execution_time,
            'results': results
        }

# FastAPI lifespan context manager (replacing deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources before startup and clean up after shutdown"""
    # Setup
    logger.debug("Starting application initialization...")
    logger.debug(f"Thread pool initialized with {thread_pool._max_workers} workers")
    DataHandler.create_sample_csv()
    logger.debug("Application startup completed successfully")
    yield
    # Cleanup
    logger.debug("Starting application shutdown...")
    logger.debug("Shutting down thread pool")
    thread_pool.shutdown()
    logger.debug("Application shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.post("/process")
async def process_request(request_id: int):
    """
    API endpoint to process a single request
    Uses thread pool for concurrent execution
    """
    logger.debug(f"API: Received request to process request_id={request_id}")
    future = thread_pool.submit(Worker.thread_worker, request_id)
    logger.debug(f"API: Submitted request {request_id} to thread pool, waiting for completion")
    result = future.result()  # Wait for completion
    logger.debug(f"API: Request {request_id} completed successfully")
    
    return result

@app.post("/process_batch")
async def process_batch(num_requests: int = 1200):
    """
    Process multiple requests concurrently
    This demonstrates handling 1200 requests with thread pool
    """
    start_time = time.time()
    
    logger.debug(f"API: Starting batch processing of {num_requests} requests")
    
    # Submit all requests to thread pool
    logger.debug(f"API: Submitting {num_requests} requests to thread pool")
    futures = [thread_pool.submit(Worker.thread_worker, i) for i in range(num_requests)]
    logger.debug(f"API: All {num_requests} requests submitted to thread pool")
    
    # Collect results as they complete
    logger.debug("API: Waiting for all requests to complete...")
    results = [future.result() for future in futures]
    
    total_time = time.time() - start_time
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    
    logger.debug(f"API: Batch processing completed in {total_time:.2f} seconds")
    logger.debug(f"API: Average execution time per request: {avg_time:.2f} seconds")
    logger.debug(f"API: Throughput: {num_requests / total_time:.2f} requests/second")
    
    return {
        'total_requests': num_requests,
        'total_time_seconds': total_time,
        'average_execution_time': avg_time,
        'throughput_requests_per_second': num_requests / total_time
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
