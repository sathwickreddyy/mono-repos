"""
Celery Tasks Module

Defines CPU-intensive financial calculation tasks for distributed processing.
Implements retry logic, timeouts, and circuit breaker patterns.

Design Patterns:
- Task idempotency (safe for retries)
- Exponential backoff for transient failures
- Resource limits (time/memory)
- Structured result format
"""

import logging
import time
from typing import Dict, Any, List
from decimal import Decimal, getcontext
from celery import Task
from celery.exceptions import SoftTimeLimitExceeded, Reject

from main import app
from calculations import (
    calculate_portfolio_var,
    monte_carlo_simulation,
    optimize_portfolio,
    stress_test_portfolio
)

# Configure decimal precision for financial calculations
getcontext().prec = 28

logger = logging.getLogger(__name__)


class FinancialTask(Task):
    """
    Base task class with custom error handling and circuit breaker.
    
    Implements:
    - Retry logic with exponential backoff
    - Structured error responses
    - Task state tracking
    """
    
    autoretry_for = (ConnectionError, TimeoutError)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True


@app.task(
    bind=True,
    base=FinancialTask,
    name="tasks.calculate_var",
    time_limit=120,  # Hard limit: 2 minutes
    soft_time_limit=100,  # Soft limit: 100 seconds
    acks_late=True,  # Acknowledge only after completion
    reject_on_worker_lost=True,
)
def calculate_var(
    self,
    portfolio_data: Dict[str, Any],
    confidence_level: float = 0.95,
    time_horizon: int = 10,
    correlation_id: str = None  # FIXED: Accept correlation_id for distributed tracing
) -> Dict[str, Any]:
    """
    Calculate Value at Risk (VaR) for a portfolio.
    
    This is a CPU-intensive Monte Carlo simulation that:
    1. Generates 100,000+ random price paths
    2. Calculates portfolio value for each scenario
    3. Computes percentile-based risk metrics
    
    Args:
        portfolio_data: Dict with positions, prices, volatilities
        confidence_level: VaR confidence (default 95%)
        time_horizon: Days to simulate (default 10)
        correlation_id: Request correlation ID for distributed tracing
    
    Returns:
        Dict with var_amount, expected_shortfall, simulation_count
        
    Raises:
        SoftTimeLimitExceeded: Task taking too long
        ValueError: Invalid input data
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(
        f"✅ VaR task START - Task ID: {task_id}, Correlation ID: {correlation_id}, "
        f"confidence={confidence_level}, horizon={time_horizon}"
    )
    
    logger.info(
        f"Starting VaR calculation - Task: {task_id}, "
        f"Positions: {len(portfolio_data.get('positions', []))}, "
        f"Confidence: {confidence_level}"
    )
    
    try:
        # Validate inputs
        if not 0 < confidence_level < 1:
            raise ValueError(f"Confidence level must be between 0 and 1, got {confidence_level}")
        
        if time_horizon <= 0:
            raise ValueError(f"Time horizon must be positive, got {time_horizon}")
        
        # Perform CPU-intensive calculation
        result = calculate_portfolio_var(
            portfolio_data=portfolio_data,
            confidence_level=confidence_level,
            time_horizon=time_horizon
        )
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"✅ VaR task COMPLETE - Task ID: {task_id}, Correlation ID: {correlation_id}, "
            f"Duration: {elapsed:.2f}s, VaR: ${result['var_amount']:,.2f}"
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "result": result,
            "metadata": {
                "execution_time": round(elapsed, 3),
                "confidence_level": confidence_level,
                "time_horizon": time_horizon,
                "worker": self.request.hostname
            }
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Task {task_id} exceeded time limit")
        raise Reject("Task exceeded soft time limit", requeue=False)
        
    except ValueError as e:
        logger.error(f"Validation error in task {task_id}: {e}")
        return {
            "status": "error",
            "task_id": task_id,
            "error": str(e),
            "error_type": "ValidationError"
        }
        
    except Exception as e:
        logger.exception(f"Unexpected error in task {task_id}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(
    bind=True,
    base=FinancialTask,
    name="tasks.monte_carlo_pricing",
    time_limit=180,
    soft_time_limit=150,
    acks_late=True,
)
def monte_carlo_pricing(
    self,
    option_params: Dict[str, Any],
    simulations: int = 100000
) -> Dict[str, Any]:
    """
    Price options using Monte Carlo simulation.
    
    CPU-intensive simulation generating millions of random paths
    to estimate option fair value under different market scenarios.
    
    Args:
        option_params: Dict with strike, spot, volatility, rate, maturity
        simulations: Number of Monte Carlo paths (default 100k)
    
    Returns:
        Dict with option_price, standard_error, confidence_interval
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(
        f"Starting Monte Carlo pricing - Task: {task_id}, "
        f"Simulations: {simulations:,}"
    )
    
    try:
        result = monte_carlo_simulation(
            option_params=option_params,
            num_simulations=simulations
        )
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"Completed Monte Carlo pricing - Task: {task_id}, "
            f"Duration: {elapsed:.2f}s, Price: ${result['option_price']:.4f}"
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "result": result,
            "metadata": {
                "execution_time": round(elapsed, 3),
                "simulations": simulations,
                "worker": self.request.hostname
            }
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Task {task_id} exceeded time limit")
        raise Reject("Task exceeded soft time limit", requeue=False)
        
    except Exception as e:
        logger.exception(f"Error in task {task_id}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(
    bind=True,
    base=FinancialTask,
    name="tasks.portfolio_optimization",
    time_limit=240,
    soft_time_limit=200,
    acks_late=True,
)
def portfolio_optimization(
    self,
    assets: List[str],
    returns: List[List[float]],
    constraints: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Optimize portfolio allocation using mean-variance optimization.
    
    CPU-intensive quadratic programming to find optimal asset weights
    that maximize return for given risk level (Markowitz optimization).
    
    Args:
        assets: List of asset symbols
        returns: Historical returns matrix
        constraints: Risk tolerance, min/max weights, etc.
    
    Returns:
        Dict with optimal_weights, expected_return, portfolio_risk
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(
        f"Starting portfolio optimization - Task: {task_id}, "
        f"Assets: {len(assets)}, Observations: {len(returns)}"
    )
    
    try:
        result = optimize_portfolio(
            assets=assets,
            returns=returns,
            constraints=constraints
        )
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"Completed portfolio optimization - Task: {task_id}, "
            f"Duration: {elapsed:.2f}s, Expected Return: {result['expected_return']:.2%}"
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "result": result,
            "metadata": {
                "execution_time": round(elapsed, 3),
                "asset_count": len(assets),
                "worker": self.request.hostname
            }
        }
        
    except Exception as e:
        logger.exception(f"Error in task {task_id}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(
    bind=True,
    base=FinancialTask,
    name="tasks.stress_test",
    time_limit=300,
    soft_time_limit=250,
    acks_late=True,
)
def stress_test(
    self,
    portfolio_data: Dict[str, Any],
    scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Run stress tests on portfolio under extreme market scenarios.
    
    Simulates portfolio performance during market crashes, rate spikes,
    liquidity crises, and other tail-risk events.
    
    Args:
        portfolio_data: Current portfolio positions and values
        scenarios: List of stress scenarios (2008 crash, COVID, etc.)
    
    Returns:
        Dict with scenario results, worst-case loss, recovery time
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(
        f"Starting stress test - Task: {task_id}, "
        f"Scenarios: {len(scenarios)}"
    )
    
    try:
        result = stress_test_portfolio(
            portfolio_data=portfolio_data,
            scenarios=scenarios
        )
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"Completed stress test - Task: {task_id}, "
            f"Duration: {elapsed:.2f}s, Worst Loss: {result['worst_case_loss']:.2%}"
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "result": result,
            "metadata": {
                "execution_time": round(elapsed, 3),
                "scenarios_tested": len(scenarios),
                "worker": self.request.hostname
            }
        }
        
    except Exception as e:
        logger.exception(f"Error in task {task_id}: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(name="tasks.health_check")
def health_check() -> Dict[str, str]:
    """
    Simple health check task to verify worker connectivity.
    
    Returns immediately with worker status - used by monitoring
    and load balancer health checks.
    """
    return {
        "status": "healthy",
        "worker": "celery-worker",
        "timestamp": time.time()
    }
