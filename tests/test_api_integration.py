"""
Integration Tests - Backend API
Tests all FastAPI endpoints against the running backend.
"""
import pytest
import httpx

BASE_URL = "http://localhost:8000"


class TestHealthEndpoint:
    def test_health_returns_200(self):
        r = httpx.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200

    def test_health_has_required_fields(self):
        r = httpx.get(f"{BASE_URL}/api/health", timeout=10)
        data = r.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "scanner_available" in data
        assert "has_cached_data" in data

    def test_scanner_available(self):
        r = httpx.get(f"{BASE_URL}/api/health", timeout=10)
        data = r.json()
        assert data["scanner_available"] is True, \
            f"Scanner not available: {data.get('scanner_error')}"


class TestConfigEndpoint:
    def test_config_returns_200(self):
        r = httpx.get(f"{BASE_URL}/api/config", timeout=10)
        assert r.status_code == 200

    def test_config_has_structure(self):
        r = httpx.get(f"{BASE_URL}/api/config", timeout=10)
        data = r.json()
        assert "exchange" in data or "timeframes" in data


class TestLatestSignalsEndpoint:
    def test_latest_returns_200(self):
        r = httpx.get(f"{BASE_URL}/api/signals/latest", timeout=10)
        assert r.status_code == 200

    def test_latest_has_success_field(self):
        r = httpx.get(f"{BASE_URL}/api/signals/latest", timeout=10)
        data = r.json()
        assert "success" in data


class TestBacktestEndpoint:
    def test_backtest_returns_200(self):
        r = httpx.post(f"{BASE_URL}/api/backtest",
                       json={"days": 30, "capital": 10000.0, "risk_pct": 1.0},
                       timeout=10)
        assert r.status_code == 200

    def test_backtest_has_results(self):
        r = httpx.post(f"{BASE_URL}/api/backtest",
                       json={"days": 30, "capital": 10000.0},
                       timeout=10)
        data = r.json()
        for key in ["days", "capital", "final_equity", "total_return_pct",
                     "n_trades", "win_rate_pct", "equity_curve", "trades"]:
            assert key in data, f"Missing: {key}"

    def test_backtest_equity_curve_not_empty(self):
        r = httpx.post(f"{BASE_URL}/api/backtest",
                       json={"days": 60, "capital": 5000.0},
                       timeout=10)
        data = r.json()
        assert len(data["equity_curve"]) > 0
        assert data["equity_curve"][0] == 5000.0

    def test_backtest_deterministic(self):
        """Same inputs → same outputs (seeded RNG)."""
        body = {"days": 30, "capital": 10000.0, "risk_pct": 1.0}
        r1 = httpx.post(f"{BASE_URL}/api/backtest", json=body, timeout=10).json()
        r2 = httpx.post(f"{BASE_URL}/api/backtest", json=body, timeout=10).json()
        assert r1["final_equity"] == r2["final_equity"]
        assert r1["win_rate_pct"] == r2["win_rate_pct"]


class TestScanEndpoint:
    """
    Integration test for the full scan pipeline.
    NOTE: This calls the real TradingView API, so may be slow (10-30s).
    """
    def test_scan_returns_200(self):
        r = httpx.post(f"{BASE_URL}/api/scan",
                       json={"exchanges": ["bybit"], "timeframes": ["15m"],
                             "min_confidence": 5},
                       timeout=120)
        assert r.status_code == 200

    def test_scan_response_structure(self):
        r = httpx.post(f"{BASE_URL}/api/scan",
                       json={"exchanges": ["bybit"], "timeframes": ["15m"],
                             "min_confidence": 5},
                       timeout=120)
        data = r.json()
        for key in ["scan_time", "exchanges", "timeframes",
                     "total_scanned", "total_signals", "signals"]:
            assert key in data, f"Missing: {key}"
        assert isinstance(data["signals"], list)

    def test_scan_signals_have_correct_shape(self):
        r = httpx.post(f"{BASE_URL}/api/scan",
                       json={"exchanges": ["bybit"], "timeframes": ["15m"],
                             "min_confidence": 5},
                       timeout=120)
        data = r.json()
        if data["signals"]:
            sig = data["signals"][0]
            for key in ["symbol", "direction", "price", "stop_loss",
                         "tp1", "confidence", "bbw", "reasons"]:
                assert key in sig, f"Signal missing: {key}"
            assert sig["direction"] in ("LONG", "SHORT")
            assert 0 <= sig["confidence"] <= 10


class TestCORSHeaders:
    def test_cors_allowed_origin(self):
        r = httpx.options(f"{BASE_URL}/api/health",
                          headers={"Origin": "http://localhost:5173",
                                   "Access-Control-Request-Method": "GET"},
                          timeout=10)
        assert r.status_code == 200
