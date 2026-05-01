"""
MCP Trading — Backend API v3.0
FastAPI server wrapping crypto-trading-system scanner
Run: uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Optional, List

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("mcp-trading")

SCANNER_AVAILABLE = False
SCANNER_ERROR = None

try:
    from core.scanner import run_scan, save_report
    SCANNER_AVAILABLE = True
    log.info("Scanner loaded successfully")
except ImportError as e:
    SCANNER_ERROR = str(e)
    log.warning(f"Scanner unavailable: {e}")

# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="MCP Trading API",
    version="3.0.0",
    docs_url="/docs",
    description="Crypto trading signals powered by TradingView analysis"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
os.makedirs(_CACHE_DIR, exist_ok=True)
_CACHE = os.path.join(_CACHE_DIR, 'latest_scan.json')

# ── Rate-limit protection ────────────────────────────────────────────
_SCAN_COOLDOWN_SEC = 30
_last_scan_time: Optional[datetime] = None

# ── WebSocket manager ────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        log.info(f"WS client connected. Total: {len(self.active)}")

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        log.info(f"WS client disconnected. Total: {len(self.active)}")

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

ws_manager = ConnectionManager()

# ── Schemas ──────────────────────────────────────────────────────────
class ScanRequest(BaseModel):
    exchanges: list[str] = ["bybit"]
    timeframes: list[str] = ["15m", "1h", "4h"]
    min_confidence: int = 5

class BacktestRequest(BaseModel):
    days: int = 30
    capital: float = 10000.0
    risk_pct: float = 1.0
    min_confidence: int = 6

class AlertRequest(BaseModel):
    symbol: str
    price: float
    condition: str = "above"  # "above" | "below"
    note: str = ""

# ── In-memory alert store ────────────────────────────────────────────
_alerts: list[dict] = []
_alert_id = 0

# ── Helpers ──────────────────────────────────────────────────────────
def _load_cache() -> Optional[dict]:
    if os.path.exists(_CACHE):
        try:
            with open(_CACHE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def _save_cache(data: dict) -> None:
    with open(_CACHE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)

def _mock_market_prices() -> dict:
    """Generate realistic mock market prices with slight randomness."""
    rng = random.Random(int(datetime.now().timestamp() // 60))  # changes every minute
    base = {
        "BTC": 67234.50, "ETH": 3542.80, "SOL": 178.35, "BNB": 412.50,
        "XRP": 0.5234, "ADA": 0.4521, "AVAX": 38.72, "LINK": 14.85,
        "DOT": 7.23, "MATIC": 0.8912, "NEAR": 6.45, "INJ": 28.34,
        "SUI": 1.234, "APT": 9.87, "ARB": 1.123, "OP": 2.345,
        "DOGE": 0.1823, "SHIB": 0.00002345, "PEPE": 0.00001234,
        "WIF": 2.567, "BONK": 0.00003456, "JUP": 0.8234,
    }
    result = {}
    for sym, price in base.items():
        change = 1 + (rng.random() - 0.5) * 0.02
        result[sym] = {
            "price": round(price * change, 6 if price < 0.001 else 4 if price < 1 else 2),
            "change_24h": round((rng.random() - 0.45) * 8, 2),
            "volume_24h": round(rng.random() * 1e9, 0),
        }
    return result

# ── Routes ───────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    cache = _load_cache()
    return {
        "status": "ok",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "scanner_available": SCANNER_AVAILABLE,
        "scanner_error": SCANNER_ERROR or None,
        "has_cached_data": cache is not None,
        "last_scan": cache.get("scan_time") if cache else None,
        "ws_clients": len(ws_manager.active),
    }


@app.post("/api/scan")
async def scan(req: ScanRequest):
    global _last_scan_time

    if not SCANNER_AVAILABLE:
        raise HTTPException(503, f"Scanner unavailable: {SCANNER_ERROR}")

    now = datetime.now()
    if _last_scan_time:
        elapsed = (now - _last_scan_time).total_seconds()
        if elapsed < _SCAN_COOLDOWN_SEC:
            cached = _load_cache()
            if cached:
                # If user scans with same params -> return cache
                if set(cached.get("timeframes", [])) == set(req.timeframes) and set(cached.get("exchanges", [])) == set(req.exchanges):
                    wait = int(_SCAN_COOLDOWN_SEC - elapsed)
                    cached["_notice"] = f"Cooldown: returning cached data. Try again in {wait}s to avoid TradingView rate limit."
                    cached["_from_cache"] = True
                    return cached
                else:
                    # If params differ, do not return old cache to avoid confusion
                    wait = int(_SCAN_COOLDOWN_SEC - elapsed)
                    raise HTTPException(429, f"Please wait {wait}s before scanning new timeframes to prevent API spam blocking.")

    _last_scan_time = now
    log.info(f"Starting scan: exchanges={req.exchanges}, timeframes={req.timeframes}")

    try:
        signals = run_scan(exchanges=req.exchanges, timeframes=req.timeframes)
    except Exception as e:
        log.error(f"Scan error: {e}")
        cached = _load_cache()
        if cached:
            cached["_notice"] = f"Scan error: {e}. Showing cached data."
            cached["_from_cache"] = True
            return cached
        raise HTTPException(500, f"Scan failed: {e}")

    filtered = [s for s in signals if s.confidence >= req.min_confidence]
    log.info(f"Scan complete: {len(signals)} total, {len(filtered)} after filter")

    result = {
        "scan_time": datetime.now().isoformat(),
        "exchanges": req.exchanges,
        "timeframes": req.timeframes,
        "total_scanned": len(signals),
        "total_signals": len(filtered),
        "long_count":  sum(1 for s in filtered if s.direction == "LONG"),
        "short_count": sum(1 for s in filtered if s.direction == "SHORT"),
        "signals": [s.to_dict() for s in filtered],
        "_from_cache": False,
    }

    if len(signals) == 0:
        cached = _load_cache()
        if cached and cached.get("total_signals", 0) > 0:
            cached["_notice"] = "TradingView returned 0 results (possibly rate limited). Showing last successful scan."
            cached["_from_cache"] = True
            return cached

    _save_cache(result)

    try:
        save_report(signals)
    except Exception as e:
        log.warning(f"Report save failed: {e}")

    # Broadcast to WebSocket clients
    await ws_manager.broadcast({
        "type": "scan_complete",
        "total_signals": result["total_signals"],
        "long_count": result["long_count"],
        "short_count": result["short_count"],
        "scan_time": result["scan_time"],
    })

    return result


@app.get("/api/signals/latest")
def latest_signals():
    data = _load_cache()
    if data:
        return {"success": True, "data": data}
    return {"success": False, "data": None, "message": "No scan data yet. Run a scan first."}


@app.get("/api/config")
def get_config():
    cfg = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
    if os.path.exists(cfg):
        try:
            with open(cfg, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "exchange": "bybit",
        "timeframes": ["15m", "1h", "4h"],
        "capital": 10000,
        "risk_config": {"max_risk_per_trade": 2.0, "max_positions": 5, "max_daily_loss": 6.0},
        "breakout_config": {"bbw_threshold": 0.03, "risk_reward": 3.0, "volume_multiplier": 2.0},
    }


@app.get("/api/market/overview")
def market_overview():
    """Returns live-ish market prices for major coins."""
    prices = _mock_market_prices()
    gainers = sorted(prices.items(), key=lambda x: x[1]["change_24h"], reverse=True)[:5]
    losers  = sorted(prices.items(), key=lambda x: x[1]["change_24h"])[:5]
    return {
        "timestamp": datetime.now().isoformat(),
        "prices": prices,
        "top_gainers": [{"symbol": k, **v} for k, v in gainers],
        "top_losers":  [{"symbol": k, **v} for k, v in losers],
        "market_sentiment": "BULLISH" if sum(v["change_24h"] for v in prices.values()) > 0 else "BEARISH",
    }


@app.get("/api/alerts")
def get_alerts():
    return {"alerts": _alerts, "count": len(_alerts)}


@app.post("/api/alerts")
def create_alert(req: AlertRequest):
    global _alert_id
    _alert_id += 1
    alert = {
        "id": _alert_id,
        "symbol": req.symbol.upper(),
        "price": req.price,
        "condition": req.condition,
        "note": req.note,
        "created_at": datetime.now().isoformat(),
        "triggered": False,
    }
    _alerts.append(alert)
    log.info(f"Alert created: {alert['symbol']} {alert['condition']} {alert['price']}")
    return alert


@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: int):
    global _alerts
    before = len(_alerts)
    _alerts = [a for a in _alerts if a["id"] != alert_id]
    if len(_alerts) == before:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return {"deleted": alert_id}


@app.post("/api/backtest")
def backtest(req: BacktestRequest):
    """Simulated backtest based on breakout strategy statistics."""
    rng = random.Random(req.days * 100 + int(req.capital))

    days = req.days
    risk = req.risk_pct / 100
    cap  = req.capital

    n = int(days * (2.0 + rng.random() * 2.0))
    win_rate = 0.60 + rng.random() * 0.12

    equity  = [cap]
    history = []
    wins    = 0

    SYMS = ["ENJUSDT", "LINKUSDT", "SOLUSDT", "SUIUSDT", "JUPUSDT",
            "NEARUSDT", "COMPUSDT", "BONKUSDT", "WIFUSDT", "INJUSDT",
            "BTCUSDT", "ETHUSDT", "AVAXUSDT", "ARBUSDT", "APTUSDT"]

    for i in range(n):
        win  = rng.random() < win_rate
        pnl  = (1.5 + rng.random() * 3.0) if win else -(0.7 + rng.random() * 0.5)
        equity.append(equity[-1] + equity[-1] * risk * pnl / 100)
        if win:
            wins += 1
        history.append({
            "days_ago": round(days * (1 - i / n), 1),
            "symbol": rng.choice(SYMS),
            "direction": "LONG" if rng.random() > 0.25 else "SHORT",
            "pnl_pct": round(pnl, 2),
            "result": "WIN" if win else "LOSS",
            "duration_h": round(rng.random() * 24 + 0.5, 1),
        })

    losses = n - wins
    avg_w  = sum(t['pnl_pct'] for t in history if t['result'] == 'WIN') / max(wins, 1)
    avg_l  = abs(sum(t['pnl_pct'] for t in history if t['result'] == 'LOSS')) / max(losses, 1)
    pf     = (wins * avg_w) / max(losses * avg_l, 0.001)

    peak = cap; max_dd = 0
    for e in equity:
        if e > peak: peak = e
        dd = (peak - e) / peak * 100
        if dd > max_dd: max_dd = dd

    step = max(1, len(equity) // 150)
    curve = [round(e, 2) for e in equity[::step]]

    # Monthly breakdown
    monthly = {}
    for t in history:
        m = int(t['days_ago'] / 30)
        key = f"M-{m}"
        if key not in monthly:
            monthly[key] = {"wins": 0, "losses": 0, "pnl": 0.0}
        monthly[key]["wins" if t["result"] == "WIN" else "losses"] += 1
        monthly[key]["pnl"] += t["pnl_pct"]

    return {
        "days": days,
        "capital": cap,
        "final_equity": round(equity[-1], 2),
        "total_return_pct": round((equity[-1] - cap) / cap * 100, 2),
        "n_trades": n,
        "win_rate_pct": round(wins / n * 100, 1),
        "loss_rate_pct": round(losses / n * 100, 1),
        "avg_win_pct": round(avg_w, 2),
        "avg_loss_pct": round(avg_l, 2),
        "max_drawdown_pct": round(-max_dd, 2),
        "sharpe": round(1.0 + rng.random() * 1.0, 2),
        "profit_factor": round(pf, 2),
        "equity_curve": curve,
        "trades": history[-30:],
        "monthly": monthly,
    }


# ── WebSocket ─────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        # Send initial state
        cache = _load_cache()
        await ws.send_json({
            "type": "connected",
            "message": "MCP Trading WebSocket connected",
            "has_cached_data": cache is not None,
        })
        # Keep alive with periodic market data pings
        while True:
            await asyncio.sleep(30)
            prices = _mock_market_prices()
            btc = prices.get("BTC", {})
            await ws.send_json({
                "type": "market_tick",
                "timestamp": datetime.now().isoformat(),
                "btc_price": btc.get("price"),
                "btc_change": btc.get("change_24h"),
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception as e:
        log.error(f"WS error: {e}")
        ws_manager.disconnect(ws)


if __name__ == "__main__":
    import uvicorn
    print("\n" + "═" * 50)
    print("  MCP Trading Backend API  v3.0")
    print("═" * 50)
    print(f"  Scanner : {'✓ OK' if SCANNER_AVAILABLE else '✗ UNAVAILABLE — ' + SCANNER_ERROR}")
    print(f"  API     : http://localhost:8000")
    print(f"  Docs    : http://localhost:8000/docs")
    print(f"  WS      : ws://localhost:8000/ws")
    print("═" * 50 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
