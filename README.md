# Multi-Factor Portfolio Backtesting

A systematic equity-research project that constructs and evaluates a monthly rebalanced multi-factor portfolio against the SPY benchmark.

## Strategy Overview

The strategy ranks a diversified universe of 30 U.S. equities using:

- Momentum: 12-month price performance
- Low Volatility: 63-day annualized volatility, ranked inversely
- Portfolio construction: Equal-weighted allocation to the top 30% of ranked stocks
- Rebalancing: Monthly at month-end
- Transaction costs: 10 basis points per unit of portfolio turnover

## Methodology

1. Download split- and dividend-adjusted daily price data using `yfinance`.
2. Calculate factor signals for each stock.
3. Combine momentum and low-volatility ranks into a composite score.
4. Select the top-scoring stocks at each month-end.
5. Apply the selected weights with a one-day execution lag.
6. Compare strategy performance with the SPY ETF benchmark.

## Project Structure

```text
multi-factor-portfolio-backtesting/
├── data/
│   ├── raw/                  # Local market data, excluded from Git
│   └── processed/            # Local processed data, excluded from Git
├── outputs/
│   ├── cumulative_performance.png
│   └── strategy_drawdown.png
├── src/
│   ├── data_loader.py
│   ├── factors.py
│   ├── performance.py
│   ├── portfolio.py
│   └── visualization.py
├── run_backtest.py
├── .gitignore
└── README.md
```

## Installation

```bash
pip install yfinance pandas numpy matplotlib statsmodels seaborn openpyxl
```

## Usage

Run the backtest from the repository root:

```bash
python run_backtest.py
```

The script downloads data if no local price file exists and saves results and charts to `outputs/`.

## Key Outputs

- `outputs/cumulative_performance.png`: Growth of $1 invested in the strategy and SPY
- `outputs/strategy_drawdown.png`: Strategy drawdown through time
- `outputs/backtest_results.csv`: Daily strategy and benchmark returns
- `outputs/performance_metrics.csv`: Return, volatility, Sharpe ratio, and maximum drawdown

## Important Notes

This project is for educational and research purposes only. Historical performance does not guarantee future results. The implementation uses publicly available market data and simplifying assumptions; it does not constitute investment advice.