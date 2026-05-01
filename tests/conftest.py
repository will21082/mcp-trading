"""
Shared fixtures for all tests.
"""
import os
import sys
import pytest

# ── Path setup so tests can import project modules ────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
TV_MCP_SRC = os.path.join(ROOT, "tradingview-mcp", "src")

for p in [BACKEND, TV_MCP_SRC]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Force UTF-8 stdout on Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


@pytest.fixture
def sample_indicators():
    """A realistic set of TradingView indicators for a bullish coin."""
    return {
        "open": 100.0,
        "close": 105.0,
        "high": 107.0,
        "low": 99.0,
        "volume": 500_000,
        "SMA20": 102.0,
        "SMA50": 100.0,
        "SMA200": 95.0,
        "BB.upper": 106.0,
        "BB.lower": 98.0,
        "EMA50": 101.0,
        "EMA200": 96.0,
        "EMA9": 104.0,
        "EMA10": 103.5,
        "EMA20": 102.5,
        "EMA30": 101.5,
        "EMA100": 98.0,
        "RSI": 55.0,
        "RSI[1]": 52.0,
        "ADX": 32.0,
        "ADX+DI": 28.0,
        "ADX-DI": 15.0,
        "MACD.macd": 1.5,
        "MACD.signal": 0.8,
        "ATR": 3.5,
        "Stoch.K": 65.0,
        "Stoch.D": 60.0,
        "CCI20": 45.0,
        "W.R": -35.0,
        "AO": 2.5,
        "AO[1]": 1.8,
        "Mom": 5.0,
        "Mom[1]": 3.0,
        "P.SAR": 99.0,
        "Ichimoku.BLine": 100.0,
        "Stoch.RSI.K": 55.0,
        "HullMA9": 103.0,
        "VWAP": 101.0,
        "VWMA": 102.0,
        "UO": 55.0,
        "volume.SMA20": 300_000,
        "Recommend.All": 0.6,
        "Recommend.MA": 0.7,
        "Recommend.Other": 0.3,
        "Pivot.M.Classic.Middle": 102.0,
        "Pivot.M.Classic.R1": 108.0,
        "Pivot.M.Classic.R2": 112.0,
        "Pivot.M.Classic.R3": 118.0,
        "Pivot.M.Classic.S1": 97.0,
        "Pivot.M.Classic.S2": 93.0,
        "Pivot.M.Classic.S3": 88.0,
    }


@pytest.fixture
def sample_bearish_indicators():
    """A realistic set of TradingView indicators for a bearish coin."""
    return {
        "open": 105.0,
        "close": 95.0,
        "high": 106.0,
        "low": 94.0,
        "volume": 600_000,
        "SMA20": 100.0,
        "SMA50": 103.0,
        "SMA200": 108.0,
        "BB.upper": 105.0,
        "BB.lower": 95.0,
        "EMA50": 104.0,
        "EMA200": 110.0,
        "RSI": 28.0,
        "ADX": 35.0,
        "MACD.macd": -2.0,
        "MACD.signal": -0.5,
    }


@pytest.fixture
def sample_metrics_bullish():
    """Pre-computed metrics for a bullish scenario."""
    return {
        "price": 105.0,
        "change": 5.0,
        "bbw": 0.0784,
        "rating": 2,
        "signal": "BUY",
    }


@pytest.fixture
def sample_metrics_squeeze():
    """Pre-computed metrics for a BB squeeze scenario."""
    return {
        "price": 100.5,
        "change": 0.5,
        "bbw": 0.02,
        "rating": 2,
        "signal": "BUY",
    }
