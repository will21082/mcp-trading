"""
Unit Tests — validators module
Tests: sanitize_timeframe, sanitize_exchange, EXCHANGE_SCREENER mapping
"""
import pytest
from tradingview_mcp.core.utils.validators import (
    sanitize_timeframe,
    sanitize_exchange,
    is_stock_exchange,
    get_market_type,
    EXCHANGE_SCREENER,
    ALLOWED_TIMEFRAMES,
)


class TestSanitizeTimeframe:
    def test_valid_timeframes(self):
        assert sanitize_timeframe("5m") == "5m"
        assert sanitize_timeframe("15m") == "15m"
        assert sanitize_timeframe("1h") == "1h"
        assert sanitize_timeframe("4h") == "4h"

    def test_case_insensitive(self):
        assert sanitize_timeframe("1D") == "1D"
        assert sanitize_timeframe("1d") == "1D"

    def test_monthly(self):
        assert sanitize_timeframe("1M") == "1M"
        assert sanitize_timeframe("1m") == "1M"

    def test_invalid_returns_default(self):
        assert sanitize_timeframe("2h") == "5m"
        assert sanitize_timeframe("abc") == "5m"

    def test_empty_returns_default(self):
        assert sanitize_timeframe("") == "5m"
        assert sanitize_timeframe(None) == "5m"

    def test_custom_default(self):
        assert sanitize_timeframe("invalid", default="1h") == "1h"


class TestSanitizeExchange:
    def test_valid_crypto_exchanges(self):
        assert sanitize_exchange("binance") == "binance"
        assert sanitize_exchange("bybit") == "bybit"
        assert sanitize_exchange("kucoin") == "kucoin"
        assert sanitize_exchange("okx") == "okx"

    def test_case_insensitive(self):
        assert sanitize_exchange("BINANCE") == "binance"
        assert sanitize_exchange("Bybit") == "bybit"

    def test_stock_exchanges(self):
        assert sanitize_exchange("bist") == "bist"
        assert sanitize_exchange("nasdaq") == "nasdaq"
        assert sanitize_exchange("nyse") == "nyse"

    def test_invalid_returns_default(self):
        assert sanitize_exchange("fake_exchange") == "kucoin"

    def test_empty_returns_default(self):
        assert sanitize_exchange("") == "kucoin"
        assert sanitize_exchange(None) == "kucoin"


class TestExchangeScreener:
    def test_crypto_exchanges_use_crypto_screener(self):
        crypto_exchanges = ["binance", "bybit", "kucoin", "okx", "coinbase", "gateio", "huobi"]
        for ex in crypto_exchanges:
            assert EXCHANGE_SCREENER[ex] == "crypto", f"{ex} should map to 'crypto'"

    def test_bist_uses_turkey(self):
        assert EXCHANGE_SCREENER["bist"] == "turkey"

    def test_nasdaq_nyse_use_america(self):
        assert EXCHANGE_SCREENER["nasdaq"] == "america"
        assert EXCHANGE_SCREENER["nyse"] == "america"

    def test_all_uses_crypto(self):
        assert EXCHANGE_SCREENER["all"] == "crypto"


class TestIsStockExchange:
    def test_stock_exchanges(self):
        assert is_stock_exchange("bist") is True
        assert is_stock_exchange("nasdaq") is True
        assert is_stock_exchange("nyse") is True
        assert is_stock_exchange("egx") is True

    def test_crypto_exchanges(self):
        assert is_stock_exchange("binance") is False
        assert is_stock_exchange("bybit") is False
        assert is_stock_exchange("kucoin") is False

    def test_case_insensitive(self):
        assert is_stock_exchange("BIST") is True
        assert is_stock_exchange("Nasdaq") is True


class TestGetMarketType:
    def test_known_exchange(self):
        assert get_market_type("binance") == "crypto"
        assert get_market_type("bist") == "turkey"

    def test_unknown_defaults_to_crypto(self):
        assert get_market_type("unknown_exchange") == "crypto"
