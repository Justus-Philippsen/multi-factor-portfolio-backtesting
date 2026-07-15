"""
Visualization functions for portfolio backtest results.
"""

from pathlib import Path

import matplotlib.pyplot as plt


OUTPUT_DIR = Path("outputs")


def plot_cumulative_returns(results):
    """Plot cumulative performance against the benchmark."""
    fig, ax = plt.subplots(figsize=(12, 6))

    results["strategy_cumulative"].plot(
        ax=ax,
        label="Multi-Factor Strategy",
        linewidth=2.2,
        color="#1f77b4",
    )
    results["benchmark_cumulative"].plot(
        ax=ax,
        label="SPY Benchmark",
        linewidth=2,
        color="#7f7f7f",
        linestyle="--",
    )

    ax.set_title("Cumulative Portfolio Performance", fontsize=15, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth of $1")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "cumulative_performance.png", dpi=300)
    plt.close(fig)


def plot_drawdown(results):
    """Plot strategy drawdown over time."""
    cumulative = results["strategy_cumulative"]
    drawdown = cumulative / cumulative.cummax() - 1

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.fill_between(
        drawdown.index,
        drawdown.values,
        0,
        color="#d62728",
        alpha=0.35,
    )
    ax.plot(drawdown.index, drawdown.values, color="#d62728", linewidth=1.5)

    ax.set_title("Multi-Factor Strategy Drawdown", fontsize=15, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "strategy_drawdown.png", dpi=300)
    plt.close(fig)


def create_all_visualizations(results):
    """Create all backtest visualizations."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plot_cumulative_returns(results)
    plot_drawdown(results)