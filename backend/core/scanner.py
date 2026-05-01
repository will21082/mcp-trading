"""
Unified Crypto Scanner
----------------------
Core Strategy: BB Squeeze + Multi-timeframe confirmation
Exit: 70% at TP1, 30% at TP2 | SL: -3% | Max hold depends on timeframe
"""
from __future__ import annotations

import os
import sys
import datetime
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tradingview-mcp', 'src'))

from tradingview_mcp.core.services.coinlist import load_symbols
from tradingview_mcp.core.services.indicators import compute_metrics
from tradingview_mcp.core.utils.validators import EXCHANGE_SCREENER
from tradingview_ta import get_multiple_analysis

REPORT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Signal:
    symbol: str
    direction: str          # "LONG" | "SHORT"
    exchange: str
    timeframe: str
    price: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3: float
    risk_reward: float
    confidence: int         # 0-10
    quality: int            # 0-15
    bbw: float
    bb_rating: int
    rsi: float
    adx: float
    above_ema50: bool
    golden_cross: bool      # price > ema50 > ema200
    macd_bullish: bool
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tp1_pct: float = 70.0   # % đóng tại TP1
    tp2_pct: float = 30.0   # % đóng tại TP2
    max_hold_hours: int = 6

    @property
    def sl_pct(self) -> float:
        return abs(self.price - self.stop_loss) / self.price * 100

    @property
    def tp1_pct_gain(self) -> float:
        if self.direction == "LONG":
            return (self.tp1 - self.price) / self.price * 100
        return (self.price - self.tp1) / self.price * 100

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "exchange": self.exchange,
            "timeframe": self.timeframe,
            "price": self.price,
            "stop_loss": round(self.stop_loss, 6),
            "tp1": round(self.tp1, 6),
            "tp2": round(self.tp2, 6),
            "tp3": round(self.tp3, 6),
            "risk_reward": round(self.risk_reward, 2),
            "confidence": self.confidence,
            "quality": self.quality,
            "bbw": round(self.bbw, 4),
            "bb_rating": self.bb_rating,
            "rsi": round(self.rsi, 1),
            "adx": round(self.adx, 1),
            "above_ema50": self.above_ema50,
            "golden_cross": self.golden_cross,
            "exit_plan": f"70% @ TP1 ({self.tp1_pct_gain:+.1f}%), 30% @ TP2, SL {self.sl_pct:.1f}%",
            "reasons": self.reasons,
            "warnings": self.warnings,
        }


# ── Scoring engine ────────────────────────────────────────────────────────────

def _score_long(ind: dict, metrics: dict, timeframe: str = "15m") -> tuple[int, int, list, list]:
    """Trả về (confidence, quality, reasons, warnings)."""
    c, q, reasons, warnings = 0, 0, [], []

    bb_rating = metrics['rating']
    bbw       = metrics['bbw']
    rsi       = ind.get('RSI', 50) or 50
    ema50     = ind.get('EMA50', 0) or 0
    ema200    = ind.get('EMA200', 0) or 0
    adx       = ind.get('ADX', 0) or 0
    macd      = ind.get('MACD.macd', 0) or 0
    macd_sig  = ind.get('MACD.signal', 0) or 0
    close     = ind.get('close', 0) or 0
    volume    = ind.get('volume', 0) or 0
    bb_upper  = ind.get('BB.upper', 0) or 0

    # --- HARD FILTERS ---
    quote_vol = close * volume
    if quote_vol < 160_000:
        return -1, -1, [], []  # Ignore low liquidity < $160k

    is_scalp = timeframe in ("1m", "3m", "5m", "15m")
    if is_scalp:
        if bbw > 0.06: return -1, -1, [], []  # Max BBW for Scalp (0.06)
        if rsi < 35 or rsi > 75: return -1, -1, [], []  # RSI bounds
        # Anti-FOMO CỰC KỲ KHẮT KHE: Giá phải nằm cách mép trên BB ít nhất 0.2% để tránh hoàn toàn pullback
        if bb_upper and close > bb_upper * 0.998: return -1, -1, [], []
    else:
        if ema200 and close < ema200: return -1, -1, [], []  # Trend must be bullish
        if bbw > 0.09: return -1, -1, [], []  # Max BBW for Swing (0.09)
        # Anti-FOMO CỰC KỲ KHẮT KHE:
        if bb_upper and close > bb_upper * 0.995: return -1, -1, [], []
    # --------------------

    # 1. BB Rating — Must be positive
    if bb_rating >= 3:
        c += 5; q += 4; reasons.append(f"🔥 BB Rating +{bb_rating} EXTREME BUY")
    elif bb_rating == 2:
        c += 4; q += 3; reasons.append(f"✅ BB Rating +{bb_rating} Strong Buy")
    elif bb_rating == 1:
        c += 2; q += 1; reasons.append(f"⬆️ BB Rating +{bb_rating} Buy")
    else:
        return -1, -1, [], []  # sentinel: skip

    # 2. BB Squeeze
    if bbw < 0.015:
        c += 4; q += 3; reasons.append(f"💥 BB Ultra Tight: {bbw:.4f}")
    elif bbw < 0.030:
        c += 3; q += 2; reasons.append(f"💥 BB Squeeze: {bbw:.4f}")
    elif bbw < 0.050:
        c += 2; q += 1; reasons.append(f"📊 BB Consolidating: {bbw:.4f}")

    # 3. RSI
    if 45 <= rsi <= 60:
        c += 3; q += 2; reasons.append(f"✅ RSI Perfect: {rsi:.1f}")
    elif 35 <= rsi <= 68:
        c += 2; q += 1; reasons.append(f"✅ RSI Good: {rsi:.1f}")
    elif rsi > 70:
        warnings.append(f"⚠️ RSI Overbought: {rsi:.1f}"); c -= 1
    elif rsi < 30:
        warnings.append(f"⚠️ RSI Oversold: {rsi:.1f}")

    # 4. EMA Structure
    if ema50 and ema200 and close > ema50 > ema200:
        c += 3; q += 2; reasons.append("💎 Golden Cross (price > EMA50 > EMA200)")
    elif ema50 and close > ema50:
        c += 2; q += 1; reasons.append("📈 Above EMA50")
    elif ema50 and close < ema50:
        warnings.append("⚠️ Below EMA50")

    # 5. ADX
    if adx > 30:
        c += 2; q += 1; reasons.append(f"💪 ADX Strong: {adx:.1f}")
    elif adx > 20:
        c += 1; reasons.append(f"📊 ADX: {adx:.1f}")

    # 6. MACD
    if macd > macd_sig:
        c += 1; reasons.append("📈 MACD Bullish")

    # 7. Volume
    if volume > 200_000:
        c += 1; reasons.append("📢 High Volume")

    return min(c, 10), min(q, 15), reasons, warnings


def _score_short(ind: dict, metrics: dict, timeframe: str = "15m") -> tuple[int, int, list, list]:
    """Trả về (confidence, quality, reasons, warnings)."""
    c, q, reasons, warnings = 0, 0, [], []

    bb_rating = metrics['rating']
    bbw       = metrics['bbw']
    rsi       = ind.get('RSI', 50) or 50
    ema50     = ind.get('EMA50', 0) or 0
    ema200    = ind.get('EMA200', 0) or 0
    adx       = ind.get('ADX', 0) or 0
    macd      = ind.get('MACD.macd', 0) or 0
    macd_sig  = ind.get('MACD.signal', 0) or 0
    close     = ind.get('close', 0) or 0
    volume    = ind.get('volume', 0) or 0
    bb_lower  = ind.get('BB.lower', 0) or 0

    # --- HARD FILTERS ---
    quote_vol = close * volume
    if quote_vol < 160_000:
        return -1, -1, [], []  # Ignore low liquidity < $160k

    is_scalp = timeframe in ("1m", "3m", "5m", "15m")
    if is_scalp:
        if bbw > 0.06: return -1, -1, [], []  # Max BBW for Scalp
        if rsi < 25 or rsi > 65: return -1, -1, [], []  # RSI bounds
        # Anti-FOMO CỰC KỲ KHẮT KHE: Giá phải nằm cách mép dưới BB ít nhất 0.2%
        if bb_lower and close < bb_lower * 1.002: return -1, -1, [], []
    else:
        if ema200 and close > ema200: return -1, -1, [], []  # Trend must be bearish
        if bbw > 0.09: return -1, -1, [], []  # Max BBW for Swing
        # Anti-FOMO CỰC KỲ KHẮT KHE:
        if bb_lower and close < bb_lower * 1.005: return -1, -1, [], []
    # --------------------

    # 1. BB Rating — Must be negative
    if bb_rating <= -3:
        c += 5; q += 4; reasons.append(f"🔥 BB Rating {bb_rating} EXTREME SELL")
    elif bb_rating == -2:
        c += 4; q += 3; reasons.append(f"❌ BB Rating {bb_rating} Strong Sell")
    elif bb_rating == -1:
        c += 2; q += 1; reasons.append(f"⬇️ BB Rating {bb_rating} Sell")
    else:
        return -1, -1, [], []  # sentinel: skip

    # 2. BB Squeeze
    if bbw < 0.015:
        c += 4; q += 3; reasons.append(f"💥 BB Ultra Tight: {bbw:.4f}")
    elif bbw < 0.030:
        c += 3; q += 2; reasons.append(f"💥 BB Squeeze: {bbw:.4f}")
    elif bbw < 0.050:
        c += 2; q += 1; reasons.append(f"📊 BB Consolidating: {bbw:.4f}")

    # 3. RSI
    if rsi > 70:
        c += 3; q += 2; reasons.append(f"🔴 RSI Overbought: {rsi:.1f}")
    elif rsi > 60:
        c += 2; q += 1; reasons.append(f"RSI Elevated: {rsi:.1f}")
    elif rsi < 30:
        warnings.append(f"⚠️ RSI Oversold: {rsi:.1f}"); c -= 1
    elif 40 <= rsi <= 55:
        c += 1; reasons.append(f"RSI Neutral: {rsi:.1f}")

    # 4. EMA Structure
    if ema50 and ema200 and close < ema50 < ema200:
        c += 3; q += 2; reasons.append("💀 Death Cross (price < EMA50 < EMA200)")
    elif ema50 and close < ema50:
        c += 2; q += 1; reasons.append("📉 Below EMA50")

    # 5. ADX
    if adx > 30:
        c += 2; q += 1; reasons.append(f"💪 ADX Strong: {adx:.1f}")
    elif adx > 20:
        c += 1

    # 6. MACD
    if macd < macd_sig:
        c += 1; reasons.append("📉 MACD Bearish")

    # 7. Volume
    if volume > 200_000:
        c += 1; reasons.append("📢 High Volume")

    return min(c, 10), min(q, 15), reasons, warnings


def _build_signal(direction: str, ind: dict, metrics: dict, symbol: str, exchange: str, tf: str,
                  confidence: int, quality: int, reasons: list, warnings: list) -> Optional[Signal]:
    close  = ind.get('close', 0) or 0
    ema50  = ind.get('EMA50', 0) or 0
    ema200 = ind.get('EMA200', 0) or 0
    adx    = ind.get('ADX', 0) or 0
    macd   = ind.get('MACD.macd', 0) or 0
    macd_s = ind.get('MACD.signal', 0) or 0

    if direction == "LONG":
        sl  = close * 0.97
        risk = close - sl
        tp1 = close + risk * 1.5   # +4.5%
        tp2 = close + risk * 2.5   # +7.5%
        tp3 = close + risk * 3.5   # +10.5%
    else:
        sl  = close * 1.03
        risk = sl - close
        tp1 = close - risk * 1.5
        tp2 = close - risk * 2.5
        tp3 = close - risk * 3.5

    rr = (risk * 2.5) / risk if risk > 0 else 0  # based on TP2

    if tf in ("1m", "3m", "5m"): max_hold = 2
    elif tf in ("15m", "30m"): max_hold = 6
    elif tf in ("1h", "2h", "4h"): max_hold = 24
    else: max_hold = 72

    return Signal(
        symbol=symbol,
        direction=direction,
        exchange=exchange,
        timeframe=tf,
        price=close,
        stop_loss=sl,
        tp1=tp1, tp2=tp2, tp3=tp3,
        risk_reward=rr,
        confidence=confidence,
        quality=quality,
        bbw=metrics['bbw'],
        bb_rating=metrics['rating'],
        rsi=ind.get('RSI', 50) or 50,
        adx=adx,
        above_ema50=close > ema50 if ema50 else False,
        golden_cross=(close > ema50 > ema200) if (ema50 and ema200) else False,
        macd_bullish=macd > macd_s,
        reasons=reasons,
        warnings=warnings,
        max_hold_hours=max_hold,
    )


# ── Core batch scanner ────────────────────────────────────────────────────────

def _batch_scan(exchange: str, timeframe: str, max_symbols: int = 400) -> list[Signal]:
    symbols = load_symbols(exchange)
    if not symbols:
        print(f"  [!] No symbols found for exchange: {exchange}")
        return []
        
    # Map to valid TradingView intervals to prevent API ignoring invalid formats
    tv_map = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
              "1h": "1h", "2h": "2h", "4h": "4h", 
              "1d": "1d", "1D": "1d", "1w": "1W", "1W": "1W", "1m": "1M"}
    api_interval = tv_map.get(timeframe, timeframe)
    
    symbols = symbols[:max_symbols]
    screener = EXCHANGE_SCREENER.get(exchange, "crypto")
    signals: list[Signal] = []
    empty_count = 0

    for i in range(0, len(symbols), 200):
        batch = symbols[i:i + 200]
        try:
            analysis = get_multiple_analysis(screener=screener, interval=api_interval, symbols=batch)
        except Exception as e:
            print(f"  [!] TradingView API error (batch {i//200+1}): {e}")
            continue

        # Check for rate limiting: if most symbols return None, TV is throttling
        batch_empty = sum(1 for v in analysis.values() if v is None)
        empty_count += batch_empty
        if batch_empty == len(batch):
            print(f"  [!] Rate limited: TradingView returned 0/{len(batch)} symbols. Wait 5-10 min.")
            continue

        for sym, data in analysis.items():
            if not data:
                continue
            try:
                ind = data.indicators
                metrics = compute_metrics(ind)
                if not metrics or metrics['bbw'] is None or metrics['bbw'] <= 0:
                    continue

                clean_sym = sym.split(":")[1] if ":" in sym else sym

                # Try LONG
                c, q, reasons, warnings = _score_long(ind, metrics, timeframe)
                if c >= 5 and q >= 4:
                    sig = _build_signal("LONG", ind, metrics, clean_sym, exchange, timeframe,
                                        c, q, reasons, warnings)
                    if sig:
                        signals.append(sig)
                        continue  # don't double-count same coin as SHORT

                # Try SHORT
                c, q, reasons, warnings = _score_short(ind, metrics, timeframe)
                if c >= 5 and q >= 4:
                    sig = _build_signal("SHORT", ind, metrics, clean_sym, exchange, timeframe,
                                        c, q, reasons, warnings)
                    if sig:
                        signals.append(sig)

            except Exception as e:
                print(f"  [!] Error scoring {sym}: {type(e).__name__}: {e}")
                continue

    return signals


# ── Public API ────────────────────────────────────────────────────────────────

def run_scan(exchanges: list[str] = None, timeframes: list[str] = None) -> list[Signal]:
    """
    Run scan on selected exchanges and timeframes.
    Default: Bybit on 15m + 1h + 4h.
    """
    if exchanges is None:
        exchanges = ["bybit"]
    if timeframes is None:
        timeframes = ["15m", "1h", "4h"]
        
    # Remove duplicate timeframes (e.g. ['1h', '1h'])
    exchanges = list(dict.fromkeys(exchanges))
    timeframes = list(dict.fromkeys(timeframes))

    all_signals: list[Signal] = []
    seen: set[str] = set()

    for exchange in exchanges:
        for tf in timeframes:
            print(f"  [*] Scanning {exchange.upper()} {tf}...")
            sigs = _batch_scan(exchange, tf)
            for s in sigs:
                # Gộp theo coin + chiều để mỗi coin chỉ hiển thị 1 lần duy nhất (khung giờ cao nhất)
                key = f"{s.symbol}_{s.direction}"
                if key not in seen:
                    all_signals.append(s)
                    seen.add(key)
                else:
                    # Replace with higher-TF version (1D > 4h > 1h > 15m > 5m)
                    tf_rank = {"1m": 0, "3m": 1, "5m": 2, "15m": 3, "30m": 4, "1h": 5, "2h": 6, "4h": 7, "1d": 8, "1D": 8, "1W": 9}
                    existing_idx = next(i for i, x in enumerate(all_signals) if f"{x.symbol}_{x.direction}" == key)
                    if tf_rank.get(tf, 0) > tf_rank.get(all_signals[existing_idx].timeframe, 0):
                        all_signals[existing_idx] = s

    # Sort: LONG first by quality desc, then SHORT by quality desc
    long_sigs  = sorted([s for s in all_signals if s.direction == "LONG"],
                        key=lambda x: (x.quality, x.confidence), reverse=True)
    short_sigs = sorted([s for s in all_signals if s.direction == "SHORT"],
                        key=lambda x: (x.quality, x.confidence), reverse=True)

    return long_sigs + short_sigs


# ── Report generator ──────────────────────────────────────────────────────────

def _fmt_signal_md(s: Signal, idx: int) -> str:
    direction_icon = "🟢 LONG" if s.direction == "LONG" else "🔴 SHORT"
    gold = " 💎 Golden Cross" if s.golden_cross else ""
    return f"""### {idx}. `{s.symbol}` — {direction_icon}{gold}

| | |
|---|---|
| **Exchange / TF** | {s.exchange.upper()} · {s.timeframe} |
| **Entry** | `{s.price:.6g}` |
| **Stop Loss** | `{s.stop_loss:.6g}` ({s.sl_pct:.1f}%) |
| **TP1** (close 70%) | `{s.tp1:.6g}` ({s.tp1_pct_gain:+.1f}%) |
| **TP2** (close 30%) | `{s.tp2:.6g}` |
| **TP3** (optional) | `{s.tp3:.6g}` |
| **R:R** | {s.risk_reward:.1f}x |
| **Confidence** | {s.confidence}/10 · Quality {s.quality}/15 |
| **BBW** | {s.bbw:.4f} · BB Rating {s.bb_rating:+d} |
| **RSI** | {s.rsi:.1f} · ADX {s.adx:.1f} |
| **Max Hold** | {s.max_hold_hours}h |

**Reasons:** {', '.join(s.reasons)}
{"**Warnings:** " + ', '.join(s.warnings) if s.warnings else ""}

"""


def save_report(signals: list[Signal]) -> str:
    now = datetime.datetime.now()
    path = os.path.join(REPORT_DIR, f"scan_{now.strftime('%Y%m%d_%H%M%S')}.md")

    long_sigs  = [s for s in signals if s.direction == "LONG"]
    short_sigs = [s for s in signals if s.direction == "SHORT"]

    lines = [f"""# 📊 Scan Report — {now.strftime('%Y-%m-%d %H:%M:%S')}

> **Strategy:** BB Squeeze + Multi-TF Confirmation
> **Exit:** 70% at TP1 · 30% at TP2 · SL -3%
> **Total Signals:** {len(long_sigs)} LONG · {len(short_sigs)} SHORT

---

## 🟢 LONG Signals ({len(long_sigs)})

"""]

    if long_sigs:
        for i, s in enumerate(long_sigs, 1):
            lines.append(_fmt_signal_md(s, i))
    else:
        lines.append("_No eligible LONG signals found._\n")

    lines.append(f"\n---\n\n## 🔴 SHORT Signals ({len(short_sigs)})\n\n")

    if short_sigs:
        for i, s in enumerate(short_sigs, 1):
            lines.append(_fmt_signal_md(s, i))
    else:
        lines.append("_No eligible SHORT signals found._\n")

    lines.append("""
---

> ⚠️ Always confirm before entering trades. Risk Management: Do not risk more than 3% per trade.
""")

    content = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crypto Scanner")
    parser.add_argument("--exchanges", nargs="+", default=["bybit"], help="Exchanges")
    parser.add_argument("--timeframes", nargs="+", default=["15m", "1h", "4h"], help="Timeframes")
    parser.add_argument("--no-report", action="store_true", help="Do not save report file")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  CRYPTO SCANNER — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Exchange: {', '.join(args.exchanges).upper()} | TF: {', '.join(args.timeframes)}")
    print(f"{'='*60}\n")

    signals = run_scan(exchanges=args.exchanges, timeframes=args.timeframes)

    long_sigs  = [s for s in signals if s.direction == "LONG"]
    short_sigs = [s for s in signals if s.direction == "SHORT"]

    print(f"\n{'='*60}")
    print(f"  [+] LONG ({len(long_sigs)})")
    print(f"{'='*60}")
    for s in long_sigs:
        gold = " (Golden)" if s.golden_cross else ""
        print(f"  {s.symbol:<15} TF:{s.timeframe:<4} C:{s.confidence}/10  Q:{s.quality}/15"
              f"  BBW:{s.bbw:.3f}  RSI:{s.rsi:.0f}  SL:{s.stop_loss:.6g}  TP1:{s.tp1:.6g}{gold}")
        print(f"    -> {' | '.join(s.reasons[:3])}")

    print(f"\n{'='*60}")
    print(f"  [-] SHORT ({len(short_sigs)})")
    print(f"{'='*60}")
    for s in short_sigs:
        print(f"  {s.symbol:<15} TF:{s.timeframe:<4} C:{s.confidence}/10  Q:{s.quality}/15"
              f"  BBW:{s.bbw:.3f}  RSI:{s.rsi:.0f}  SL:{s.stop_loss:.6g}  TP1:{s.tp1:.6g}")
        print(f"    -> {' | '.join(s.reasons[:3])}")

    if not args.no_report:
        path = save_report(signals)
        print(f"\n[OK] Report: {path}")
    else:
        print(f"\n[OK] Total: {len(signals)} signals")
