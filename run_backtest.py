"""
Run the multi-factor portfolio backtest and create outputs.
"""

from pathlib import Path

import pandas as pd

from src.data_loader import load_prices
from src.performance import create_performance_table
from src.portfolio import (
    calculate_benchmark_returns,
    calculate_portfolio_returns,
    create_monthly_weights,
)
from src.visualization import create_all_visualizations


OUTPUT_DIR = Path("outputs")
RESULTS_PATH = OUTPUT_DIR / "backtest_results.csv"
METRICS_PATH = OUTPUT_DIR / "performance_metrics.csv"


def main():
    """Run the strategy, calculate metrics, and save all outputs."""
    prices = load_prices()
    weights = create_monthly_weights(prices)

    strategy_returns = calculate_portfolio_returns(prices, weights)
    benchmark_returns = calculate_benchmark_returns(prices)

    results = pd.DataFrame(
        {
            "strategy_return": strategy_returns,
            "benchmark_return": benchmark_returns,
        }
    ).dropna()

    results["strategy_cumulative"] = (1 + results["strategy_return"]).cumprod()
    results["benchmark_cumulative"] = (1 + results["benchmark_return"]).cumprod()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_PATH)

    metrics = create_performance_table(results)
    metrics.to_csv(METRICS_PATH)

    create_all_visualizations(results)

    print("Backtest completed successfully.")
    print(f"Results saved to: {RESULTS_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")
    print("\nPerformance metrics:")
    print(metrics.round(4))


if __name__ == "__main__":
    main()