"""
Financial Calculations Module

Implements CPU-intensive financial algorithms:
- Value at Risk (VaR) via Monte Carlo simulation
- Option pricing (Black-Scholes Monte Carlo)
- Portfolio optimization (Markowitz mean-variance)
- Stress testing (scenario analysis)

These calculations are deliberately CPU-intensive to demonstrate
the benefits of distributed task processing.
"""

import math
import time
import random
from typing import Dict, Any, List, Tuple
from decimal import Decimal
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize


def calculate_portfolio_var(
    portfolio_data: Dict[str, Any],
    confidence_level: float = 0.95,
    time_horizon: int = 10
) -> Dict[str, Any]:
    """
    Calculate Value at Risk using Monte Carlo simulation.
    
    VaR estimates the maximum loss over a time period at a given
    confidence level (e.g., 95% confident we won't lose more than $X).
    
    Algorithm:
    1. Extract portfolio positions and parameters
    2. Generate 100,000+ correlated random price paths
    3. Calculate portfolio value for each scenario
    4. Compute percentile-based VaR and Expected Shortfall
    
    Args:
        portfolio_data: {
            'positions': [{'symbol': 'AAPL', 'quantity': 100, 'price': 150.0}],
            'volatilities': {'AAPL': 0.25, 'GOOGL': 0.30},
            'correlations': [[1.0, 0.7], [0.7, 1.0]]
        }
        confidence_level: Probability level (default 0.95)
        time_horizon: Days to simulate (default 10)
    
    Returns:
        {
            'var_amount': float,  # VaR in dollars
            'expected_shortfall': float,  # Average loss beyond VaR
            'simulation_count': int,
            'percentile': float
        }
    """
    start = time.time()
    
    # Extract data
    positions = portfolio_data.get('positions', [])
    volatilities = portfolio_data.get('volatilities', {})
    correlations = portfolio_data.get('correlations', None)
    
    # Portfolio value
    portfolio_value = sum(pos['quantity'] * pos['price'] for pos in positions)
    
    # Number of simulations (CPU-intensive)
    num_simulations = 100000
    
    # Generate correlated random returns
    num_assets = len(positions)
    
    if correlations is None:
        # Default: uncorrelated assets
        correlations = np.identity(num_assets)
    else:
        correlations = np.array(correlations)
    
    # Cholesky decomposition for correlated random variables
    try:
        cholesky = np.linalg.cholesky(correlations)
    except np.linalg.LinAlgError:
        # If correlation matrix is not positive definite, use identity
        cholesky = np.identity(num_assets)
    
    # Simulate portfolio returns
    simulated_returns = []
    
    for _ in range(num_simulations):
        # Generate independent standard normal random variables
        z = np.random.standard_normal(num_assets)
        
        # Apply correlation structure
        correlated_z = cholesky @ z
        
        # Calculate returns for each asset
        portfolio_return = 0.0
        
        for i, pos in enumerate(positions):
            symbol = pos['symbol']
            weight = (pos['quantity'] * pos['price']) / portfolio_value
            vol = volatilities.get(symbol, 0.20)  # Default 20% volatility
            
            # Return = volatility * random_shock * sqrt(time_horizon)
            asset_return = vol * correlated_z[i] * math.sqrt(time_horizon / 252)
            portfolio_return += weight * asset_return
        
        simulated_returns.append(portfolio_return)
    
    # Sort returns (losses are negative)
    simulated_returns.sort()
    
    # Calculate VaR (percentile of loss distribution)
    var_index = int((1 - confidence_level) * num_simulations)
    var_return = simulated_returns[var_index]
    var_amount = abs(var_return * portfolio_value)
    
    # Calculate Expected Shortfall (average of losses beyond VaR)
    tail_losses = simulated_returns[:var_index]
    if tail_losses:
        expected_shortfall_return = sum(tail_losses) / len(tail_losses)
        expected_shortfall = abs(expected_shortfall_return * portfolio_value)
    else:
        expected_shortfall = var_amount
    
    elapsed = time.time() - start
    
    return {
        'var_amount': round(var_amount, 2),
        'expected_shortfall': round(expected_shortfall, 2),
        'portfolio_value': round(portfolio_value, 2),
        'simulation_count': num_simulations,
        'confidence_level': confidence_level,
        'time_horizon_days': time_horizon,
        'computation_time': round(elapsed, 3)
    }


def monte_carlo_simulation(
    option_params: Dict[str, Any],
    num_simulations: int = 100000
) -> Dict[str, Any]:
    """
    Price European options using Monte Carlo simulation.
    
    Simulates future stock prices under geometric Brownian motion,
    calculates option payoffs, and discounts to present value.
    
    Args:
        option_params: {
            'spot_price': 100.0,
            'strike_price': 105.0,
            'volatility': 0.25,
            'risk_free_rate': 0.05,
            'time_to_maturity': 1.0,  # Years
            'option_type': 'call'  # or 'put'
        }
        num_simulations: Number of price paths
    
    Returns:
        {
            'option_price': float,
            'standard_error': float,
            'confidence_interval': (lower, upper)
        }
    """
    start = time.time()
    
    S0 = option_params['spot_price']
    K = option_params['strike_price']
    sigma = option_params['volatility']
    r = option_params['risk_free_rate']
    T = option_params['time_to_maturity']
    option_type = option_params.get('option_type', 'call')
    
    # Simulate terminal stock prices
    payoffs = []
    
    for _ in range(num_simulations):
        # Generate random price path (geometric Brownian motion)
        z = random.gauss(0, 1)
        ST = S0 * math.exp((r - 0.5 * sigma ** 2) * T + sigma * math.sqrt(T) * z)
        
        # Calculate payoff
        if option_type == 'call':
            payoff = max(ST - K, 0)
        else:  # put
            payoff = max(K - ST, 0)
        
        payoffs.append(payoff)
    
    # Discount average payoff to present value
    option_price = math.exp(-r * T) * (sum(payoffs) / num_simulations)
    
    # Calculate standard error
    payoffs_array = np.array(payoffs)
    std_dev = np.std(payoffs_array)
    standard_error = std_dev / math.sqrt(num_simulations)
    
    # 95% confidence interval
    confidence_interval = (
        option_price - 1.96 * standard_error,
        option_price + 1.96 * standard_error
    )
    
    elapsed = time.time() - start
    
    return {
        'option_price': round(option_price, 4),
        'standard_error': round(standard_error, 4),
        'confidence_interval': tuple(round(x, 4) for x in confidence_interval),
        'simulations': num_simulations,
        'computation_time': round(elapsed, 3)
    }


def optimize_portfolio(
    assets: List[str],
    returns: List[List[float]],
    constraints: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Find optimal portfolio weights using mean-variance optimization.
    
    Implements Markowitz portfolio theory: maximize expected return
    for a given level of risk (or minimize risk for target return).
    
    Args:
        assets: ['AAPL', 'GOOGL', 'MSFT', ...]
        returns: Historical returns matrix (time x assets)
        constraints: {
            'target_return': 0.10,  # 10% annual return
            'risk_free_rate': 0.02,
            'max_weight': 0.30,  # Max 30% in any asset
            'min_weight': 0.05   # Min 5% in any asset
        }
    
    Returns:
        {
            'optimal_weights': {'AAPL': 0.25, 'GOOGL': 0.35, ...},
            'expected_return': 0.12,
            'portfolio_risk': 0.18,
            'sharpe_ratio': 0.55
        }
    """
    start = time.time()
    
    returns_array = np.array(returns)
    num_assets = len(assets)
    
    # Calculate mean returns and covariance matrix
    mean_returns = np.mean(returns_array, axis=0)
    cov_matrix = np.cov(returns_array, rowvar=False)
    
    # Extract constraints
    target_return = constraints.get('target_return', None)
    risk_free_rate = constraints.get('risk_free_rate', 0.02)
    max_weight = constraints.get('max_weight', 1.0)
    min_weight = constraints.get('min_weight', 0.0)
    
    # Objective function: minimize portfolio variance
    def portfolio_variance(weights):
        return weights.T @ cov_matrix @ weights
    
    # Constraint: weights sum to 1
    def weight_sum(weights):
        return np.sum(weights) - 1.0
    
    # Constraint: target return (if specified)
    def portfolio_return(weights):
        return weights.T @ mean_returns
    
    constraints_list = [
        {'type': 'eq', 'fun': weight_sum}
    ]
    
    if target_return is not None:
        constraints_list.append({
            'type': 'eq',
            'fun': lambda w: portfolio_return(w) - target_return
        })
    
    # Bounds: min_weight <= weight <= max_weight
    bounds = tuple((min_weight, max_weight) for _ in range(num_assets))
    
    # Initial guess: equal weights
    initial_weights = np.array([1.0 / num_assets] * num_assets)
    
    # Solve optimization problem
    result = minimize(
        portfolio_variance,
        initial_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints_list,
        options={'maxiter': 1000}
    )
    
    if result.success:
        optimal_weights = result.x
        expected_return = portfolio_return(optimal_weights)
        portfolio_risk = math.sqrt(portfolio_variance(optimal_weights))
        sharpe_ratio = (expected_return - risk_free_rate) / portfolio_risk
        
        weights_dict = {
            assets[i]: round(optimal_weights[i], 4)
            for i in range(num_assets)
        }
    else:
        # Optimization failed, return equal weights
        weights_dict = {asset: round(1.0 / num_assets, 4) for asset in assets}
        expected_return = np.mean(mean_returns)
        portfolio_risk = 0.0
        sharpe_ratio = 0.0
    
    elapsed = time.time() - start
    
    return {
        'optimal_weights': weights_dict,
        'expected_return': round(expected_return, 4),
        'portfolio_risk': round(portfolio_risk, 4),
        'sharpe_ratio': round(sharpe_ratio, 4),
        'optimization_success': result.success,
        'computation_time': round(elapsed, 3)
    }


def stress_test_portfolio(
    portfolio_data: Dict[str, Any],
    scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Simulate portfolio performance under extreme market scenarios.
    
    Tests portfolio resilience during historical crisis events
    (2008 crash, COVID-19, tech bubble, etc.).
    
    Args:
        portfolio_data: Current positions and values
        scenarios: [
            {
                'name': '2008 Financial Crisis',
                'equity_shock': -0.35,  # -35% equities
                'volatility_shock': 2.5,  # Volatility spikes 2.5x
                'correlation_shock': 0.9  # Correlations → 0.9
            }
        ]
    
    Returns:
        {
            'scenario_results': [{scenario, loss, recovery_time}, ...],
            'worst_case_loss': -0.42,
            'avg_loss': -0.23
        }
    """
    start = time.time()
    
    positions = portfolio_data.get('positions', [])
    portfolio_value = sum(pos['quantity'] * pos['price'] for pos in positions)
    
    scenario_results = []
    
    for scenario in scenarios:
        scenario_name = scenario['name']
        equity_shock = scenario.get('equity_shock', 0.0)
        vol_shock = scenario.get('volatility_shock', 1.0)
        
        # Calculate portfolio loss under scenario
        scenario_value = 0.0
        
        for pos in positions:
            # Apply equity shock to each position
            shocked_price = pos['price'] * (1 + equity_shock)
            scenario_value += pos['quantity'] * shocked_price
        
        loss = (scenario_value - portfolio_value) / portfolio_value
        
        # Estimate recovery time (simplified model)
        # Larger losses take longer to recover
        recovery_months = abs(loss) * 24  # Rule of thumb
        
        scenario_results.append({
            'scenario': scenario_name,
            'loss_percentage': round(loss, 4),
            'loss_amount': round(scenario_value - portfolio_value, 2),
            'recovery_months': round(recovery_months, 1)
        })
    
    # Summary statistics
    losses = [r['loss_percentage'] for r in scenario_results]
    worst_case_loss = min(losses) if losses else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    
    elapsed = time.time() - start
    
    return {
        'scenario_results': scenario_results,
        'worst_case_loss': round(worst_case_loss, 4),
        'avg_loss': round(avg_loss, 4),
        'scenarios_tested': len(scenarios),
        'computation_time': round(elapsed, 3)
    }
