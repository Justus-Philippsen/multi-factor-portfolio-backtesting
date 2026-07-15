"""
Portfolio construction and multi-factor signal generation.
"""

import numpy as np
import pandas as pd

from src.factors import (
    BENCHMARK,
    FACTOR_WEIGHTS,
    LOOKBACK_MOMENTUM,
    LOOKBACK_VOLATILITY,
    REBALANCE_FREQUENCY,
    TICKERS,
    TOP_QUANTILE,
    TRANSACTION_COST_BPS,
)


def calculate_signals(prices):
    """Calculate momentum, low-volatility, and composite signals."""
    asset_prices = prices[TICKERS].copy()
    daily_returns = asset_prices.pct_change()

    momentum = asset_prices.pct_change(LOOKBACK_MOMENTUM)
    volatility = daily_returns.rolling(LOOKBACK_VOLATILITY).std() * np.sqrt(252)

    momentum_rank = momentum.rank(axis=1, pct=True)
    low_volatility_rank = (-volatility).rank(axis=1, pct=True)

    composite_score = (
        FACTOR_WEIGHTS["momentum"] * momentum_rank
        + FACTOR_WEIGHTS["low_volatility"] * low_volatility_rank
    )

    return momentum, volatility, composite_score


def create_monthly_weights(prices):
    """Select top-scoring stocks and assign equal weights each month-end."""
    _, _, composite_score = calculate_signals(prices)

    rebalance_scores = composite_score.resample(REBALANCE_FREQUENCY).last()
    weights = pd.DataFrame(0.0, index=rebalance_scores.index, columns=TICKERS)

    for date, scores in rebalance_scores.iterrows():
        valid_scores = scores.dropna()
        number_selected = max(1, int(np.ceil(len(valid_scores) * TOP_QUANTILE)))
        selected = valid_scores.nlargest(number_selected).index
        weights.loc[date, selected] = 1 / number_selected

    return weights


def calculate_portfolio_returns(prices, weights):
    """Calculate net daily strategy returns using prior rebalance weights."""
    asset_returns = prices[TICKERS].pct_change().fillna(0)
    daily_weights = weights.reindex(asset_returns.index, method="ffill").shift(1)

    gross_returns = (daily_weights * asset_returns).sum(axis=1)
    turnover = daily_weights.diff().abs().sum(axis=1).fillna(0)
    transaction_cost = turnover * (TRANSACTION_COST_BPS / 10_000)

    return gross_returns - transaction_cost


def calculate_benchmark_returns(prices):
    """Calculate daily benchmark returns."""
    return prices[BENCHMARK].pct_change().fillna(0)