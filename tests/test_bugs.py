"""
Bug Hunter Tests - Edge cases designed to expose real bugs in the system.
These tests focus on logic errors, boundary conditions, and hidden issues.
"""
import pytest
import sys
import io
from core.scanner import Signal, _score_long, _score_short, _build_signal
from tradingview_mcp.core.services.indicators import compute_metrics, compute_bbw


# ══════════════════════════════════════════════════════════════════════════════
# BUG #1: Risk-Reward is ALWAYS 2.5 — hardcoded, never changes
# Line 249: rr = (risk * 2.5) / risk → always equals 2.5
# ══════════════════════════════════════════════════════════════════════════════
class TestBugRiskRewardHardcoded:
    def test_rr_always_2_5_regardless_of_prices(self):
        """Risk:Reward should vary based on actual TP/SL, but it's always 2.5."""
        ind1 = {"close": 100.0, "RSI": 50.0}
        ind2 = {"close": 50000.0, "RSI": 50.0}
        metrics = {"bbw": 0.02, "rating": 2}

        sig1 = _build_signal("LONG", ind1, metrics, "A", "bybit", "1h", 7, 6, [], [])
        sig2 = _build_signal("LONG", ind2, metrics, "B", "bybit", "1h", 7, 6, [], [])

        # BUG: Both have identical R:R because (risk*2.5)/risk = 2.5 always
        assert sig1.risk_reward == 2.5, "R:R is hardcoded to 2.5"
        assert sig2.risk_reward == 2.5, "R:R is hardcoded to 2.5"
        # This is a bug because R:R should be dynamic


# ══════════════════════════════════════════════════════════════════════════════
# BUG #2: RSI "dead zone" — RSI 68-70 gets NO score in LONG scoring
# Line 127-134: elif chain has gap between 68 and 70
# ══════════════════════════════════════════════════════════════════════════════
class TestBugRSIDeadZoneLong:
    def test_rsi_69_gets_no_score(self):
        """RSI=69 falls between 'good' (35-68) and 'overbought' (>70) — no score."""
        ind = {"RSI": 69.0, "close": 105.0, "volume": 100}
        metrics = {"rating": 2, "bbw": 0.04}
        c, q, reasons, warnings = _score_long(ind, metrics)

        # BB Rating +2 gives c=4, q=3
        # RSI=69 gets NOTHING (not in 35-68, not >70, not <30)
        rsi_mentioned = any("RSI" in r for r in reasons)
        rsi_warned = any("RSI" in w for w in warnings)
        assert not rsi_mentioned and not rsi_warned, \
            "BUG CONFIRMED: RSI=69 is in dead zone — no score, no warning"


# ══════════════════════════════════════════════════════════════════════════════
# BUG #3: RSI "dead zones" in SHORT scoring — RSI 55-60 and RSI 30-40
# Line 194-202: elif chain has two gaps
# ══════════════════════════════════════════════════════════════════════════════
class TestBugRSIDeadZoneShort:
    def test_rsi_57_gets_no_score(self):
        """RSI=57 falls between 'neutral' (40-55) and 'elevated' (>60)."""
        ind = {"RSI": 57.0, "close": 95.0, "volume": 100}
        metrics = {"rating": -2, "bbw": 0.04}
        c, q, reasons, warnings = _score_short(ind, metrics)

        rsi_mentioned = any("RSI" in r for r in reasons)
        assert not rsi_mentioned, \
            "BUG CONFIRMED: RSI=57 is in dead zone for SHORT scoring"

    def test_rsi_35_gets_no_score(self):
        """RSI=35 falls between 'oversold' (<30) and 'neutral' (40-55)."""
        ind = {"RSI": 35.0, "close": 95.0, "volume": 100}
        metrics = {"rating": -2, "bbw": 0.04}
        c, q, reasons, warnings = _score_short(ind, metrics)

        rsi_mentioned = any("RSI" in r for r in reasons)
        rsi_warned = any("RSI" in w for w in warnings)
        assert not rsi_mentioned and not rsi_warned, \
            "BUG CONFIRMED: RSI=35 is in dead zone for SHORT scoring"


# ══════════════════════════════════════════════════════════════════════════════
# BUG #4: Emoji in reasons/warnings will crash Windows console if printed
# Scoring functions store emoji in reasons[], but Windows cp1252 can't encode
# ══════════════════════════════════════════════════════════════════════════════
class TestBugEmojiInReasons:
    def test_reasons_contain_emoji_that_crash_on_windows(self):
        """Reasons contain emoji chars that WILL crash print() on Windows."""
        ind = {"RSI": 52.0, "EMA50": 98.0, "EMA200": 90.0,
               "ADX": 35.0, "MACD.macd": 2.0, "MACD.signal": 1.0,
               "close": 105.0, "volume": 500_000}
        metrics = {"rating": 3, "bbw": 0.012}
        c, q, reasons, warnings = _score_long(ind, metrics)

        # Check that reasons contain non-ASCII emoji characters
        has_emoji = False
        for r in reasons:
            if any(ord(ch) > 127 for ch in r):
                has_emoji = True
                break
        assert has_emoji, "BUG CONFIRMED: reasons contain emoji that crash on Windows"

        # Verify they CANNOT be encoded in cp1252 (Windows default)
        for r in reasons:
            try:
                r.encode('cp1252')
            except UnicodeEncodeError:
                # BUG: This reason string will crash if printed on Windows
                return  # Test passes — bug confirmed
        pytest.fail("Expected at least one reason to fail cp1252 encoding")


# ══════════════════════════════════════════════════════════════════════════════
# BUG #5: _batch_scan silently swallows ALL exceptions (line 322)
# Any bug inside the scoring loop is invisible — no logging, no trace
# ══════════════════════════════════════════════════════════════════════════════
class TestBugSilentExceptions:
    def test_exception_handling_is_too_broad(self):
        """_batch_scan catches Exception and continues — bugs are invisible."""
        # Simulate: if compute_metrics returns unexpected data
        ind = {"RSI": 52.0, "close": 100.0}
        metrics_with_missing_key = {"bbw": 0.02}  # missing 'rating' key

        # _score_long will crash with KeyError('rating')
        with pytest.raises(KeyError):
            _score_long(ind, metrics_with_missing_key)

        # BUG: In _batch_scan, this KeyError is silently caught and ignored
        # The developer will never know there was an error


# ══════════════════════════════════════════════════════════════════════════════
# BUG #6: _build_signal with close=0 produces garbage signal
# ══════════════════════════════════════════════════════════════════════════════
class TestBugZeroPrice:
    def test_zero_close_produces_zero_signal(self):
        """If close=0, all prices become 0 — a meaningless signal."""
        ind = {"close": 0.0, "RSI": 50.0}
        metrics = {"bbw": 0.02, "rating": 2}
        sig = _build_signal("LONG", ind, metrics, "X", "bybit", "1h", 7, 6, [], [])

        # BUG: Signal is created with all zero prices — should be rejected
        assert sig.price == 0.0
        assert sig.stop_loss == 0.0
        assert sig.tp1 == 0.0
        # _build_signal should return None for close=0


# ══════════════════════════════════════════════════════════════════════════════
# BUG #7: `ind.get('RSI', 50) or 50` treats RSI=0 as missing
# Line 99: `or 50` means if RSI is actually 0.0, it gets replaced by 50
# ══════════════════════════════════════════════════════════════════════════════
class TestBugFalsyIndicatorValues:
    def test_rsi_zero_treated_as_missing(self):
        """RSI=0.0 is falsy in Python, so `or 50` replaces it with 50."""
        ind = {"RSI": 0.0, "close": 100.0, "volume": 100}
        metrics = {"rating": 2, "bbw": 0.04}
        c, q, reasons, warnings = _score_long(ind, metrics)

        # BUG: RSI=0 should mean extremely oversold, but code treats it as RSI=50
        # The `or 50` fallback kicks in for any falsy value (0, 0.0, None, "")
        # This is incorrect — RSI=0 is a valid (extreme) value

    def test_adx_zero_treated_as_missing(self):
        """ADX=0.0 is valid but treated as missing by `or 0`."""
        ind = {"ADX": 0.0, "close": 100.0, "RSI": 50.0}
        metrics = {"rating": 1, "bbw": 0.04}
        # ADX=0 means no trend — `or 0` doesn't change it here
        # But volume=0 is same issue
        ind2 = {"volume": 0, "close": 100.0, "RSI": 50.0}
        c, q, reasons, _ = _score_long(ind2, {"rating": 1, "bbw": 0.04})
        vol_mentioned = any("Volume" in r for r in reasons)
        assert not vol_mentioned  # volume=0 should NOT trigger "High Volume"


# ══════════════════════════════════════════════════════════════════════════════
# BUG #8: compute_metrics returns None silently for missing BB data
# But compute_bbw with negative SMA still computes (no validation)
# ══════════════════════════════════════════════════════════════════════════════
class TestBugNegativeSMA:
    def test_negative_sma_produces_negative_bbw(self):
        """Negative SMA (invalid) still produces a result instead of None."""
        result = compute_bbw(sma=-100, bb_upper=105, bb_lower=95)
        # BUG: Returns -0.1 instead of None — SMA can never be negative
        assert result is not None  # This passes, showing the bug exists
        assert result < 0  # Negative BBW is meaningless


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY: Run all bug tests
# ══════════════════════════════════════════════════════════════════════════════
