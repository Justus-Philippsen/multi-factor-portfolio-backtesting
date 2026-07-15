"""
Performance and risk metrics for backtest results.
"""

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def calculate_metrics(returns):
    """Calculate annualized return, volatility, Sharpe ratio, and drawdown."""
    returns = returns.dropna()

    cumulative = (1 + returns).cumprod()
    years = len(returns) / TRADING_DAYS

    annualized_return = cumulative.iloc[-1] ** (1 / years) - 1
    annualized_volatility = returns.std() * np.sqrt(TRADING_DAYS)
    sharpe_ratio = (
        returns.mean() / returns.std() * np.sqrt(TRADING_DAYS)
        if returns.std() != 0
        else np.nan
    )

    running_peak = cumulative.cummax()
    drawdown = cumulative / running_peak - 1
    max_drawdown = drawdown.min()

    return {
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Maximum Drawdown": max_drawdown,
    }


def create_performance_table(results):
    """Create side-by-side metrics for strategy and benchmark."""
    strategy_metrics = calculate_metrics(results["strategy_return"])
    benchmark_metrics = calculate_metrics(results["benchmark_return"])

    table = pd.DataFrame(
        {
            "Multi-Factor Strategy": strategy_metrics,
            "SPY Benchmark": benchmark_metrics,
        }
    )

    table.loc["Annualized Excess Return"] = (
        table.loc["Annualized Return", "Multi-Factor Strategy"]
        - table.loc["Annualized Return", "SPY Benchmark"]
    )

    return table