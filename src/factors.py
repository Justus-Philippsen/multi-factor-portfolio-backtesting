"""
Definitions and settings for the multi-factor equity strategy.
"""

TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "BRK-B", "JPM", "V", "LLY",
    "XOM", "UNH", "MA", "COST", "HD",
    "PG", "AVGO", "JNJ", "MRK", "ABBV",
    "KO", "PEP", "WMT", "BAC", "CVX",
    "ADBE", "CRM", "NFLX", "AMD", "ORCL"
]

BENCHMARK = "SPY"
START_DATE = "2015-01-01"
END_DATE = None

LOOKBACK_MOMENTUM = 252
LOOKBACK_VOLATILITY = 63
REBALANCE_FREQUENCY = "ME"

TOP_QUANTILE = 0.30
TRANSACTION_COST_BPS = 10

FACTOR_WEIGHTS = {
    "momentum": 0.50,
    "low_volatility": 0.30,
    "quality": 0.20,
}