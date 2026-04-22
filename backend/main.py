"""
MCP Trading — Backend API
FastAPI server wrapping crypto-trading-system scanner
Run: uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import json
import os
import random
import sys
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Path setup ──────────────────────────────────────────────────────
_SYSTEM = os.path.join(os.path.dirname(__file__), '..', 'crypto-trading-system')
sys.path.insert(0, _SYSTEM)

SCANNER_AVAILABLE = False
SCANNER_ERROR = ""
try:
    from scanner import run_scan, save_report
    SCANNER_AVAILABLE = True
except ImportError as e:
    SCANNER_ERROR = str(e)

# ── App ─────────────────────────────────────────────────────────────
app = FastAPI(title="MCP Trading API", version="2.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_CACHE = os.path.join(os.path.dirname(__file__), 'cache', 'latest_scan.json')
os.makedirs(os.path.dirname(_CACHE), exist_ok=True)

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

# ── Helpers ──────────────────────────────────────────────────────────
def _load_cache() -> Optional[dict]:
    if os.path.exists(_CACHE):
        with open(_CACHE) as f:
            return json.load(f)
    return None

def _save_cache(data: dict) -> None:
    with open(_CACHE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# ── Routes ───────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    cache = _load_cache()
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "scanner_available": SCANNER_AVAILABLE,
        "scanner_error": SCANNER_ERROR or None,
        "has_cached_data": cache is not None,
        "last_scan": cache.get("scan_time") if cache else None,
    }


@app.post("/api/scan")
def scan(req: ScanRequest):
    if not SCANNER_AVAILABLE:
        raise HTTPException(503, f"Scanner unavailable: {SCANNER_ERROR}")

    signals = run_scan(exchanges=req.exchanges, timeframes=req.timeframes)
    filtered = [s for s in signals if s.confidence >= req.min_confidence]

    result = {
        "scan_time": datetime.now().isoformat(),
        "exchanges": req.exchanges,
        "timeframes": req.timeframes,
        "total_scanned": len(signals),
        "total_signals": len(filtered),
        "long_count":  sum(1 for s in filtered if s.direction == "LONG"),
        "short_count": sum(1 for s in filtered if s.direction == "SHORT"),
        "signals": [s.to_dict() for s in filtered],
    }

    _save_cache(result)

    try:
        save_report(signals)
    except Exception:
        pass

    return result


@app.get("/api/signals/latest")
def latest_signals():
    data = _load_cache()
    if data:
        return {"success": True, "data": data}
    return {"success": False, "data": None, "message": "No scan data yet. Run a scan first."}


@app.get("/api/config")
def get_config():
    cfg = os.path.join(_SYSTEM, 'config', 'settings.json')
    if os.path.exists(cfg):
        with open(cfg) as f:
            return json.load(f)
    return {
        "exchange": "bybit",
        "timeframes": ["15m", "1h", "4h"],
        "capital": 10000,
        "risk_config": {"max_risk_per_trade": 2.0, "max_positions": 5, "max_daily_loss": 6.0},
        "breakout_config": {"bbw_threshold": 0.03, "risk_reward": 3.0, "volume_multiplier": 2.0},
    }


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
            "NEARUSDT", "COMPUSDT", "BONKUSDT", "WIFUSDT", "INJUSDT"]

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

    # Downsample equity curve to max 100 points
    step = max(1, len(equity) // 100)
    curve = [round(e, 2) for e in equity[::step]]

    return {
        "days": days,
        "capital": cap,
        "final_equity": round(equity[-1], 2),
        "total_return_pct": round((equity[-1] - cap) / cap * 100, 2),
        "n_trades": n,
        "win_rate_pct": round(wins / n * 100, 1),
        "max_drawdown_pct": round(-max_dd, 2),
        "sharpe": round(1.0 + rng.random() * 1.0, 2),
        "profit_factor": round(pf, 2),
        "equity_curve": curve,
        "trades": history[-25:],
    }


if __name__ == "__main__":
    import uvicorn
    print("\n  MCP Trading Backend API")
    print(f"  Scanner : {'OK' if SCANNER_AVAILABLE else 'UNAVAILABLE — ' + SCANNER_ERROR}")
    print(f"  API     : http://localhost:8000")
    print(f"  Docs    : http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
