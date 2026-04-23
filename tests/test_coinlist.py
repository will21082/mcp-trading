"""
Unit Tests — coinlist module
Tests: load_symbols for various exchanges
"""
import pytest
from tradingview_mcp.core.services.coinlist import load_symbols


class TestLoadSymbols:
    def test_bybit_returns_symbols(self):
        symbols = load_symbols("bybit")
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        # Each symbol should contain exchange prefix
        assert any("BYBIT:" in s for s in symbols)

    def test_binance_returns_symbols(self):
        symbols = load_symbols("binance")
        assert isinstance(symbols, list)
        assert len(symbols) > 0

    def test_kucoin_returns_symbols(self):
        symbols = load_symbols("kucoin")
        assert isinstance(symbols, list)
        assert len(symbols) > 0

    def test_nonexistent_exchange_returns_empty(self):
        symbols = load_symbols("fake_exchange_xyz")
        assert symbols == []

    def test_symbols_are_strings(self):
        symbols = load_symbols("bybit")
        for s in symbols[:10]:
            assert isinstance(s, str)
            assert len(s.strip()) > 0

    def test_no_empty_lines(self):
        symbols = load_symbols("bybit")
        for s in symbols:
            assert s.strip() != ""
