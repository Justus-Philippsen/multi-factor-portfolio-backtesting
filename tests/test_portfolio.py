import numpy as np
import pandas as pd
import pytest

from src.factors import TICKERS
from src.performance import create_performance_table
from src.portfolio import calculate_portfolio_returns, create_monthly_weights


def make_prices(periods=320):
    """Create deterministic synthetic prices for fast unit tests."""
    dates = pd.bdate_range("2020-01-01", periods=periods)
    price_data = {}

    for index, ticker in enumerate(TICKERS):
        daily_return = 0.0002 + (index * 0.00001)
        price_data[ticker] = 100 * (1 + daily_return) ** np.arange(periods)

    price_data["SPY"] = 100 * 1.0003 ** np.arange(periods)
    return pd.DataFrame(price_data, index=dates)


def test_monthly_weights_sum_to_one_after_signals_are_available():
    prices = make_prices()
    weights = create_monthly_weights(prices)

    active_weights = weights[weights.sum(axis=1) > 0]
    assert not active_weights.empty
    assert np.allclose(active_weights.sum(axis=1).to_numpy(), 1.0)


def test_transaction_cost_reduces_returns(monkeypatch):
    prices = make_prices()
    weights = create_monthly_weights(prices)

    monkeypatch.setattr("src.portfolio.TRANSACTION_COST_BPS", 0)
    returns_without_costs = calculate_portfolio_returns(prices, weights)

    monkeypatch.setattr("src.portfolio.TRANSACTION_COST_BPS", 100)
    returns_with_costs = calculate_portfolio_returns(prices, weights)

    assert returns_with_costs.sum() <= returns_without_costs.sum()


def test_performance_table_contains_required_metrics():
    dates = pd.bdate_range("2024-01-01", periods=10)
    results = pd.DataFrame(
        {
            "strategy_return": [0.001] * 10,
            "benchmark_return": [0.0005] * 10,
        },
        index=dates,
    )

    metrics = create_performance_table(results)

    expected_rows = {
        "Annualized Return",
        "Annualized Volatility",
        "Sharpe Ratio",
        "Maximum Drawdown",
        "Annualized Excess Return",
    }

    assert expected_rows.issubset(metrics.index)
    assert list(metrics.columns) == ["Multi-Factor Strategy", "SPY Benchmark"]