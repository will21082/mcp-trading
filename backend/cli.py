#!/usr/bin/env python3
"""
Crypto Trading System — Entry Point
Dùng: python main.py [--exchanges bybit kucoin] [--timeframes 15m 1h 4h] [--no-report]
"""
import sys
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.scanner import run_scan, save_report
from core.risk_manager import RiskManager, print_portfolio_summary


def main():
    parser = argparse.ArgumentParser(description="Crypto Trading System")
    parser.add_argument("--exchanges",   nargs="+", default=["bybit"],
                        help="Sàn giao dịch (bybit kucoin ...)")
    parser.add_argument("--timeframes",  nargs="+", default=["15m", "1h", "4h"],
                        help="Timeframes cần scan")
    parser.add_argument("--no-report",   action="store_true",
                        help="Không lưu file .md report")
    parser.add_argument("--portfolio",   action="store_true",
                        help="Chỉ xem trạng thái portfolio, không scan")
    parser.add_argument("--capital",     type=float, default=None,
                        help="Vốn hiện tại (USD) để tính position size")
    args = parser.parse_args()

    rm = RiskManager({"capital": args.capital} if args.capital else {})
    rm.load_state()

    if args.portfolio:
        print_portfolio_summary(rm.get_portfolio_summary())
        return

    # ── Run scan ──────────────────────────────────────────────────────────────
    signals = run_scan(exchanges=args.exchanges, timeframes=args.timeframes)

    long_sigs  = [s for s in signals if s.direction == "LONG"]
    short_sigs = [s for s in signals if s.direction == "SHORT"]

    # ── Print summary ─────────────────────────────────────────────────────────
    SEP = "=" * 65
    print(f"\n{SEP}")
    print(f"  🟢 LONG SIGNALS ({len(long_sigs)})")
    print(SEP)
    for s in long_sigs:
        gold = "💎 " if s.golden_cross else ""
        can_open, _ = rm.can_open_position()
        pos_size = rm.calculate_position_size(s.price, s.stop_loss) if can_open else 0
        print(f"  {gold}{s.symbol:<14} TF:{s.timeframe:<4}  C:{s.confidence}/10  Q:{s.quality}/15"
              f"  RSI:{s.rsi:.0f}  BBW:{s.bbw:.3f}")
        print(f"    Entry:{s.price:.6g}  SL:{s.stop_loss:.6g}  TP1:{s.tp1:.6g}  TP2:{s.tp2:.6g}"
              f"  R:R {s.risk_reward:.1f}x  Size:{pos_size:.1f}%")
        print(f"    {' | '.join(s.reasons[:3])}")
        if s.warnings:
            print(f"    ⚠️  {' | '.join(s.warnings)}")

    print(f"\n{SEP}")
    print(f"  🔴 SHORT SIGNALS ({len(short_sigs)})")
    print(SEP)
    for s in short_sigs:
        can_open, _ = rm.can_open_position()
        pos_size = rm.calculate_position_size(s.price, s.stop_loss) if can_open else 0
        print(f"  {s.symbol:<14} TF:{s.timeframe:<4}  C:{s.confidence}/10  Q:{s.quality}/15"
              f"  RSI:{s.rsi:.0f}  BBW:{s.bbw:.3f}")
        print(f"    Entry:{s.price:.6g}  SL:{s.stop_loss:.6g}  TP1:{s.tp1:.6g}  TP2:{s.tp2:.6g}"
              f"  R:R {s.risk_reward:.1f}x  Size:{pos_size:.1f}%")
        print(f"    {' | '.join(s.reasons[:3])}")
        if s.warnings:
            print(f"    ⚠️  {' | '.join(s.warnings)}")

    # ── Save report ───────────────────────────────────────────────────────────
    if not args.no_report and signals:
        path = save_report(signals)
        print(f"\n✅ Report: {path}")
    elif not signals:
        print(f"\n⚠️  Không tìm thấy tín hiệu đủ điều kiện.")

    rm.save_state()


if __name__ == "__main__":
    main()
