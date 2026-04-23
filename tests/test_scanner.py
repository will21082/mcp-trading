"""
Unit Tests - scanner module
Tests: Signal dataclass, _score_long, _score_short, _build_signal
"""
import pytest
from scanner import Signal, _score_long, _score_short, _build_signal


class TestSignalDataclass:
    def test_create_long(self):
        sig = Signal(symbol="BTCUSDT", direction="LONG", exchange="bybit",
                     timeframe="4h", price=100.0, stop_loss=97.0,
                     tp1=104.5, tp2=107.5, tp3=110.5, risk_reward=2.5,
                     confidence=8, quality=10, bbw=0.025, bb_rating=2,
                     rsi=55.0, adx=30.0, above_ema50=True,
                     golden_cross=True, macd_bullish=True, reasons=["test"], warnings=[])
        assert sig.symbol == "BTCUSDT"
        assert sig.direction == "LONG"

    def test_sl_pct(self):
        sig = Signal(symbol="X", direction="LONG", exchange="bybit",
                     timeframe="1h", price=100.0, stop_loss=97.0,
                     tp1=104.5, tp2=107.5, tp3=110.5, risk_reward=2.5,
                     confidence=7, quality=8, bbw=0.02, bb_rating=2,
                     rsi=50.0, adx=25.0, above_ema50=True,
                     golden_cross=False, macd_bullish=True)
        assert sig.sl_pct == pytest.approx(3.0)

    def test_to_dict_keys(self):
        sig = Signal(symbol="ETHUSDT", direction="LONG", exchange="binance",
                     timeframe="15m", price=3000.0, stop_loss=2910.0,
                     tp1=3135.0, tp2=3225.0, tp3=3315.0, risk_reward=2.5,
                     confidence=6, quality=5, bbw=0.018, bb_rating=1,
                     rsi=48.0, adx=22.0, above_ema50=True,
                     golden_cross=False, macd_bullish=True,
                     reasons=["BB +1"], warnings=["RSI low"])
        d = sig.to_dict()
        for key in ["symbol", "direction", "price", "stop_loss", "tp1", "tp2",
                     "tp3", "confidence", "quality", "exit_plan", "reasons"]:
            assert key in d, f"Missing: {key}"


class TestScoreLong:
    def test_high_confidence(self):
        ind = {"RSI": 52.0, "EMA50": 98.0, "EMA200": 90.0,
               "ADX": 35.0, "MACD.macd": 2.0, "MACD.signal": 1.0,
               "close": 105.0, "volume": 500_000}
        c, q, reasons, _ = _score_long(ind, {"rating": 3, "bbw": 0.012})
        assert c >= 5
        assert q >= 4

    def test_neutral_bb_skips(self):
        c, q, _, _ = _score_long({"RSI": 50.0, "close": 100.0}, {"rating": 0, "bbw": 0.03})
        assert c == -1

    def test_negative_bb_skips(self):
        c, _, _, _ = _score_long({"RSI": 50.0, "close": 100.0}, {"rating": -1, "bbw": 0.03})
        assert c == -1


class TestScoreShort:
    def test_bearish(self):
        ind = {"RSI": 75.0, "EMA50": 110.0, "EMA200": 115.0,
               "ADX": 30.0, "MACD.macd": -2.0, "MACD.signal": -0.5,
               "close": 95.0, "volume": 500_000}
        c, q, _, _ = _score_short(ind, {"rating": -3, "bbw": 0.015})
        assert c >= 5
        assert q >= 4

    def test_positive_bb_skips(self):
        c, _, _, _ = _score_short({"RSI": 50.0, "close": 100.0}, {"rating": 1, "bbw": 0.03})
        assert c == -1


class TestBuildSignal:
    def test_long_prices(self):
        ind = {"close": 100.0, "EMA50": 98.0, "EMA200": 90.0,
               "ADX": 25.0, "MACD.macd": 1.0, "MACD.signal": 0.5, "RSI": 50.0}
        sig = _build_signal("LONG", ind, {"bbw": 0.025, "rating": 2},
                            "TEST", "bybit", "4h", 7, 6, ["test"], [])
        assert sig.stop_loss == pytest.approx(97.0)
        assert sig.tp1 == pytest.approx(104.5)
        assert sig.max_hold_hours == 48

    def test_short_prices(self):
        ind = {"close": 100.0, "EMA50": 105.0, "EMA200": 110.0,
               "ADX": 25.0, "MACD.macd": -1.0, "MACD.signal": -0.5, "RSI": 70.0}
        sig = _build_signal("SHORT", ind, {"bbw": 0.025, "rating": -2},
                            "TEST", "bybit", "15m", 7, 6, ["test"], [])
        assert sig.stop_loss == pytest.approx(103.0)
        assert sig.tp1 == pytest.approx(95.5)
        assert sig.max_hold_hours == 6
