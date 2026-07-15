"""
Parameter sensitivity analysis for the multi-factor equity strategy.
"""

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data_loader import load_prices
from src.factors import BENCHMARK, TICKERS
from src.performance import calculate_metrics


OUTPUT_PATH = Path("outputs/sensitivity_analysis.csv")
HEATMAP_PATH = Path("outputs/sensitivity_heatmap.png")

MOMENTUM_WINDOWS = [126, 252, 504]
VOLATILITY_WINDOWS = [21, 63, 126]
TOP_QUANTILES = [0.20, 0.30, 0.40]
TRANSACTION_COSTS_BPS = [0, 10, 25]


def calculate_returns(
    prices,
    momentum_window,
    volatility_window,
    top_quantile,
    transaction_cost_bps,
):
    """Run one parameterized momentum and low-volatility backtest."""
    asset_prices = prices[TICKERS].copy()
    asset_returns = asset_prices.pct_change().fillna(0)

    momentum = asset_prices.pct_change(momentum_window)
    volatility = (
        asset_returns.rolling(volatility_window).std() * np.sqrt(252)
    )

    composite_score = (
        0.60 * momentum.rank(axis=1, pct=True)
        + 0.40 * (-volatility).rank(axis=1, pct=True)
    )

    rebalance_scores = composite_score.resample("ME").last()
    weights = pd.DataFrame(
        0.0,
        index=rebalance_scores.index,
        columns=TICKERS,
    )

    for date, scores in rebalance_scores.iterrows():
        valid_scores = scores.dropna()
        number_selected = max(
            1,
            int(np.ceil(len(valid_scores) * top_quantile)),
        )
        selected = valid_scores.nlargest(number_selected).index
        weights.loc[date, selected] = 1 / number_selected

    daily_weights = weights.reindex(asset_returns.index, method="ffill").shift(1)
    gross_returns = (daily_weights * asset_returns).sum(axis=1)
    turnover = daily_weights.diff().abs().sum(axis=1).fillna(0)
    costs = turnover * (transaction_cost_bps / 10_000)

    return gross_returns - costs

def create_sharpe_heatmap(results):
    """Create a robustness heatmap for the base-cost, base-breadth setting."""
    base_case = results[
        (results["top_quantile"] == 0.30)
        & (results["transaction_cost_bps"] == 10)
    ]

    heatmap_data = base_case.pivot(
        index="volatility_window_days",
        columns="momentum_window_days",
        values="sharpe_ratio",
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        linewidths=0.5,
        cbar_kws={"label": "Annualized Sharpe Ratio"},
        ax=ax,
    )

    ax.set_title(
        "Strategy Robustness: Sharpe Ratio Across Lookback Windows",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Momentum Lookback (Trading Days)")
    ax.set_ylabel("Volatility Lookback (Trading Days)")

    fig.tight_layout()
    fig.savefig(HEATMAP_PATH, dpi=300)
    plt.close(fig)
def main():
    """Evaluate the full parameter grid and save performance metrics."""
    prices = load_prices()
    benchmark_returns = prices[BENCHMARK].pct_change().fillna(0)
    rows = []

    parameter_grid = product(
        MOMENTUM_WINDOWS,
        VOLATILITY_WINDOWS,
        TOP_QUANTILES,
        TRANSACTION_COSTS_BPS,
    )

    for momentum, volatility, quantile, costs in parameter_grid:
        strategy_returns = calculate_returns(
            prices=prices,
            momentum_window=momentum,
            volatility_window=volatility,
            top_quantile=quantile,
            transaction_cost_bps=costs,
        )

        metrics = calculate_metrics(strategy_returns)
        excess_return = (
            metrics["Annualized Return"]
            - calculate_metrics(benchmark_returns)["Annualized Return"]
        )

        rows.append(
            {
                "momentum_window_days": momentum,
                "volatility_window_days": volatility,
                "top_quantile": quantile,
                "transaction_cost_bps": costs,
                "annualized_return": metrics["Annualized Return"],
                "annualized_volatility": metrics["Annualized Volatility"],
                "sharpe_ratio": metrics["Sharpe Ratio"],
                "maximum_drawdown": metrics["Maximum Drawdown"],
                "annualized_excess_return_vs_spy": excess_return,
            }
        )

    results = pd.DataFrame(rows).sort_values(
        "sharpe_ratio",
        ascending=False,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_PATH, index=False)
    create_sharpe_heatmap(results)

    print("Sensitivity analysis completed successfully.")
    print(f"Results saved to: {OUTPUT_PATH}")
    print("\nTop 10 configurations by Sharpe ratio:")
    print(results.head(10).round(4).to_string(index=False))


if __name__ == "__main__":
    main()