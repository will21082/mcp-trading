"""
Integration Tests - Frontend connectivity
Tests that the Vite dev server proxies correctly to backend.
"""
import pytest
import httpx

FRONTEND_URL = "http://localhost:5173"


class TestFrontendProxy:
    def test_frontend_serves_html(self):
        r = httpx.get(FRONTEND_URL, timeout=10)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_proxy_health_through_frontend(self):
        """Vite should proxy /api/* to backend :8000."""
        r = httpx.get(f"{FRONTEND_URL}/api/health", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"

    def test_proxy_config_through_frontend(self):
        r = httpx.get(f"{FRONTEND_URL}/api/config", timeout=10)
        assert r.status_code == 200

    def test_proxy_backtest_through_frontend(self):
        r = httpx.post(f"{FRONTEND_URL}/api/backtest",
                       json={"days": 10, "capital": 1000.0},
                       timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "final_equity" in data
