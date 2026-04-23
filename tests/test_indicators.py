"""
Unit Tests — tradingview_mcp indicators module
Tests: compute_bbw, compute_bb_rating_signal, compute_metrics, extract_extended_indicators
"""
import pytest
from tradingview_mcp.core.services.indicators import (
    compute_bbw,
    compute_bb_rating_signal,
    compute_change,
    compute_metrics,
    extract_extended_indicators,
)


# ──────────────────────────────────────────────────────────────────────────────
# compute_change
# ──────────────────────────────────────────────────────────────────────────────
class TestComputeChange:
    def test_positive_change(self):
        assert compute_change(100, 105) == pytest.approx(5.0)

    def test_negative_change(self):
        assert compute_change(100, 95) == pytest.approx(-5.0)

    def test_zero_open(self):
        assert compute_change(0, 100) == 0.0

    def test_no_change(self):
        assert compute_change(50, 50) == pytest.approx(0.0)


# ──────────────────────────────────────────────────────────────────────────────
# compute_bbw
# ──────────────────────────────────────────────────────────────────────────────
class TestComputeBBW:
    def test_normal_bbw(self):
        result = compute_bbw(sma=100, bb_upper=105, bb_lower=95)
        assert result == pytest.approx(0.1)

    def test_tight_squeeze(self):
        result = compute_bbw(sma=100, bb_upper=101, bb_lower=99)
        assert result == pytest.approx(0.02)

    def test_zero_sma_returns_none(self):
        assert compute_bbw(sma=0, bb_upper=105, bb_lower=95) is None

    def test_none_sma_returns_none(self):
        assert compute_bbw(sma=None, bb_upper=105, bb_lower=95) is None


# ──────────────────────────────────────────────────────────────────────────────
# compute_bb_rating_signal
# ──────────────────────────────────────────────────────────────────────────────
class TestComputeBBRating:
    def test_extreme_buy(self):
        """Price above upper band → rating +3."""
        rating, signal = compute_bb_rating_signal(close=110, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == 3

    def test_strong_buy(self):
        """Price above midpoint of middle-upper → rating +2."""
        rating, signal = compute_bb_rating_signal(close=103, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == 2
        assert signal == "BUY"

    def test_buy(self):
        """Price above middle but below midpoint → rating +1."""
        rating, signal = compute_bb_rating_signal(close=101, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == 1

    def test_extreme_sell(self):
        """Price below lower band → rating -3."""
        rating, signal = compute_bb_rating_signal(close=90, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == -3

    def test_strong_sell(self):
        """Price below midpoint of lower-middle → rating -2."""
        rating, signal = compute_bb_rating_signal(close=96, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == -2
        assert signal == "SELL"

    def test_sell(self):
        """Price below middle → rating -1."""
        rating, signal = compute_bb_rating_signal(close=99, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == -1

    def test_neutral_at_middle(self):
        """Price exactly at middle → rating 0."""
        rating, signal = compute_bb_rating_signal(close=100, bb_upper=105, bb_middle=100, bb_lower=95)
        assert rating == 0
        assert signal == "NEUTRAL"


# ──────────────────────────────────────────────────────────────────────────────
# compute_metrics
# ──────────────────────────────────────────────────────────────────────────────
class TestComputeMetrics:
    def test_valid_indicators(self, sample_indicators):
        result = compute_metrics(sample_indicators)
        assert result is not None
        assert "price" in result
        assert "change" in result
        assert "bbw" in result
        assert "rating" in result
        assert "signal" in result

    def test_price_correctness(self, sample_indicators):
        result = compute_metrics(sample_indicators)
        assert result["price"] == 105.0

    def test_bbw_calculation(self, sample_indicators):
        """BBW = (upper - lower) / SMA20 = (106 - 98) / 102 ≈ 0.0784"""
        result = compute_metrics(sample_indicators)
        assert result["bbw"] == pytest.approx(0.0784, abs=0.001)

    def test_rating_positive(self, sample_indicators):
        """close=105 > midpoint(102, 106)=104 → rating = +2."""
        result = compute_metrics(sample_indicators)
        assert result["rating"] == 2

    def test_missing_key_returns_none(self):
        result = compute_metrics({"open": 100})
        assert result is None

    def test_empty_dict_returns_none(self):
        result = compute_metrics({})
        assert result is None


# ──────────────────────────────────────────────────────────────────────────────
# extract_extended_indicators
# ──────────────────────────────────────────────────────────────────────────────
class TestExtractExtendedIndicators:
    def test_returns_all_sections(self, sample_indicators):
        result = extract_extended_indicators(sample_indicators)
        expected_keys = [
            "rsi", "obv", "sma", "ema", "atr", "macd",
            "volume", "bollinger_bands", "support_resistance",
            "stochastic", "stochastic_rsi", "adx", "cci",
            "williams_r", "awesome_oscillator", "momentum",
            "parabolic_sar", "ichimoku", "hull_ma",
            "ultimate_oscillator", "tv_recommendation",
            "market_structure",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_rsi_signal(self, sample_indicators):
        result = extract_extended_indicators(sample_indicators)
        assert result["rsi"]["value"] == 55.0
        assert result["rsi"]["signal"] == "Neutral"

    def test_macd_crossover(self, sample_indicators):
        result = extract_extended_indicators(sample_indicators)
        assert result["macd"]["crossover"] == "Bullish"

    def test_volume_above_average(self, sample_indicators):
        result = extract_extended_indicators(sample_indicators)
        assert result["volume"]["signal"] in ("Above Average", "High", "Very High")

    def test_market_structure_bullish(self, sample_indicators):
        result = extract_extended_indicators(sample_indicators)
        assert result["market_structure"]["trend"] == "Bullish"
