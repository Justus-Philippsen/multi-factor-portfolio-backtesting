"""
Download and prepare historical market data.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

from src.factors import BENCHMARK, END_DATE, START_DATE, TICKERS


RAW_DATA_PATH = Path("data/raw/adjusted_close_prices.csv")


def download_prices():
    """Download adjusted daily close prices for assets and benchmark."""
    symbols = TICKERS + [BENCHMARK]

    prices = yf.download(
        tickers=symbols,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False,
    )["Close"]

    prices = prices.dropna(how="all").sort_index()
    return prices


def save_prices(prices):
    """Save downloaded prices locally for reproducibility."""
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(RAW_DATA_PATH)


def load_prices():
    """Load saved price data or download it when absent."""
    if RAW_DATA_PATH.exists():
        prices = pd.read_csv(RAW_DATA_PATH, index_col=0, parse_dates=True)
    else:
        prices = download_prices()
        save_prices(prices)

    return prices