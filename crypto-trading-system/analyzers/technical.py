"""
Module phân tích kỹ thuật sử dụng TradingView MCP Server
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add parent directory to path for MCP imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tradingview-mcp" / "src"))

from tradingview_mcp.server import (
    top_gainers,
    top_losers,
    coin_analysis,
    bollinger_scan,
    volume_breakout_scanner,
    rating_filter
)


@dataclass
class TechnicalSignal:
    """Tín hiệu kỹ thuật"""
    symbol: str
    signal_type: str  # BUY, SELL, NEUTRAL
    strength: int  # 1-10
    price: float
    indicators: Dict
    reasons: List[str]
    timestamp: str

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "price": self.price,
            "indicators": self.indicators,
            "reasons": self.reasons,
            "timestamp": self.timestamp
        }


class TechnicalAnalyzer:
    """Phân tích kỹ thuật toàn diện"""

    def __init__(self, exchange: str = "KUCOIN"):
        self.exchange = exchange

    def analyze_coin(self, symbol: str, timeframe: str = "15m") -> Optional[TechnicalSignal]:
        """
        Phân tích một coin cụ thể

        Args:
            symbol: Tên coin (VD: BTCUSDT)
            timeframe: Khung thời gian (5m, 15m, 1h, 4h, 1D)

        Returns:
            TechnicalSignal hoặc None nếu không có dữ liệu
        """
        try:
            # Lấy dữ liệu từ MCP server
            data = coin_analysis(symbol=symbol, exchange=self.exchange, timeframe=timeframe)

            if "error" in data:
                print(f"❌ Error analyzing {symbol}: {data['error']}")
                return None

            # Phân tích các indicators
            signal_type, strength, reasons = self._analyze_indicators(data)

            return TechnicalSignal(
                symbol=data.get("symbol", symbol),
                signal_type=signal_type,
                strength=strength,
                price=data.get("price_data", {}).get("current_price", 0),
                indicators=self._extract_key_indicators(data),
                reasons=reasons,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"❌ Exception analyzing {symbol}: {e}")
            return None

    def _analyze_indicators(self, data: Dict) -> Tuple[str, int, List[str]]:
        """
        Phân tích các indicators và đưa ra tín hiệu

        Returns:
            (signal_type, strength, reasons)
        """
        reasons = []
        buy_signals = 0
        sell_signals = 0
        strength = 0

        # 1. Bollinger Bands Analysis
        bb_rating = data.get("bollinger_analysis", {}).get("rating", 0)
        bb_position = data.get("bollinger_analysis", {}).get("position", "")
        bbw = data.get("bollinger_analysis", {}).get("bbw", 0)

        if bb_rating >= 2:
            buy_signals += 2
            reasons.append(f"📈 Bollinger Rating: +{bb_rating} (Strong Buy)")
        elif bb_rating >= 1:
            buy_signals += 1
            reasons.append(f"↗️ Bollinger Rating: +{bb_rating} (Weak Buy)")
        elif bb_rating <= -2:
            sell_signals += 2
            reasons.append(f"📉 Bollinger Rating: {bb_rating} (Strong Sell)")
        elif bb_rating <= -1:
            sell_signals += 1
            reasons.append(f"↘️ Bollinger Rating: {bb_rating} (Weak Sell)")

        # Bollinger Band Width - squeeze detection
        if bbw < 0.02:
            buy_signals += 1
            reasons.append(f"🔥 BB Squeeze detected (BBW: {bbw:.4f}) - Breakout incoming!")

        # 2. RSI Analysis
        rsi = data.get("technical_indicators", {}).get("rsi", 50)
        rsi_signal = data.get("technical_indicators", {}).get("rsi_signal", "")

        if rsi < 30:
            buy_signals += 2
            reasons.append(f"💰 RSI Oversold: {rsi:.1f} - Buy opportunity")
        elif rsi < 40:
            buy_signals += 1
            reasons.append(f"⬇️ RSI Low: {rsi:.1f} - Potential buy")
        elif rsi > 70:
            sell_signals += 2
            reasons.append(f"⚠️ RSI Overbought: {rsi:.1f} - Take profit zone")
        elif rsi > 60:
            sell_signals += 1
            reasons.append(f"⬆️ RSI High: {rsi:.1f} - Consider selling")

        # 3. MACD Analysis
        macd_div = data.get("technical_indicators", {}).get("macd_divergence", 0)
        if macd_div > 0:
            buy_signals += 1
            reasons.append(f"📊 MACD Bullish divergence: {macd_div:.6f}")
        elif macd_div < 0:
            sell_signals += 1
            reasons.append(f"📊 MACD Bearish divergence: {macd_div:.6f}")

        # 4. Trend Strength (ADX)
        adx = data.get("technical_indicators", {}).get("adx", 0)
        trend_strength = data.get("technical_indicators", {}).get("trend_strength", "")
        if adx > 25:
            if bb_rating > 0:
                buy_signals += 1
                reasons.append(f"💪 Strong uptrend (ADX: {adx:.1f})")
            elif bb_rating < 0:
                sell_signals += 1
                reasons.append(f"💪 Strong downtrend (ADX: {adx:.1f})")

        # 5. Price vs Moving Averages
        price = data.get("price_data", {}).get("current_price", 0)
        ema50 = data.get("technical_indicators", {}).get("ema50", 0)
        ema200 = data.get("technical_indicators", {}).get("ema200", 0)

        if price and ema50 and ema200:
            if price > ema50 > ema200:
                buy_signals += 2
                reasons.append(f"🚀 Golden Cross: Price > EMA50 > EMA200")
            elif price < ema50 < ema200:
                sell_signals += 2
                reasons.append(f"💀 Death Cross: Price < EMA50 < EMA200")

        # 6. Volume Analysis
        volume = data.get("price_data", {}).get("volume", 0)
        if volume > 100000:  # High volume
            if buy_signals > sell_signals:
                buy_signals += 1
                reasons.append(f"📢 High volume confirmation: {volume:,.0f}")

        # Determine signal
        total_signals = buy_signals + sell_signals
        if total_signals == 0:
            return "NEUTRAL", 0, ["No clear signals"]

        if buy_signals > sell_signals:
            signal_type = "BUY"
            strength = min(10, int((buy_signals / total_signals) * 10))
        elif sell_signals > buy_signals:
            signal_type = "SELL"
            strength = min(10, int((sell_signals / total_signals) * 10))
        else:
            signal_type = "NEUTRAL"
            strength = 5

        return signal_type, strength, reasons

    def _extract_key_indicators(self, data: Dict) -> Dict:
        """Trích xuất các indicators quan trọng"""
        return {
            "price": data.get("price_data", {}).get("current_price"),
            "change_percent": data.get("price_data", {}).get("change_percent"),
            "volume": data.get("price_data", {}).get("volume"),
            "rsi": data.get("technical_indicators", {}).get("rsi"),
            "bb_rating": data.get("bollinger_analysis", {}).get("rating"),
            "bbw": data.get("bollinger_analysis", {}).get("bbw"),
            "adx": data.get("technical_indicators", {}).get("adx"),
            "ema50": data.get("technical_indicators", {}).get("ema50"),
            "ema200": data.get("technical_indicators", {}).get("ema200"),
        }

    def scan_market(self, timeframe: str = "15m", limit: int = 20) -> List[TechnicalSignal]:
        """
        Quét thị trường tìm cơ hội

        Args:
            timeframe: Khung thời gian
            limit: Số lượng coin tối đa

        Returns:
            List các TechnicalSignal
        """
        signals = []

        print(f"🔍 Scanning {self.exchange} market ({timeframe})...")

        # 1. Tìm top gainers
        print("📈 Finding top gainers...")
        gainers = top_gainers(exchange=self.exchange, timeframe=timeframe, limit=limit)

        for coin in gainers[:10]:  # Analyze top 10
            symbol = coin["symbol"].split(":")[1] if ":" in coin["symbol"] else coin["symbol"]
            signal = self.analyze_coin(symbol, timeframe)
            if signal and signal.signal_type == "BUY" and signal.strength >= 6:
                signals.append(signal)

        # 2. Tìm BB squeeze
        print("🔥 Finding Bollinger Band squeeze...")
        squeeze_coins = bollinger_scan(
            exchange=self.exchange,
            timeframe=timeframe,
            bbw_threshold=0.03,
            limit=limit
        )

        for coin in squeeze_coins[:10]:
            symbol = coin["symbol"].split(":")[1] if ":" in coin["symbol"] else coin["symbol"]
            signal = self.analyze_coin(symbol, timeframe)
            if signal and signal.signal_type == "BUY" and signal.strength >= 6:
                signals.append(signal)

        # 3. Tìm volume breakouts
        print("💥 Finding volume breakouts...")
        volume_coins = volume_breakout_scanner(
            exchange=self.exchange,
            timeframe=timeframe,
            volume_multiplier=2.0,
            price_change_min=3.0,
            limit=limit
        )

        for coin in volume_coins[:10]:
            symbol = coin["symbol"].split(":")[1] if ":" in coin["symbol"] else coin["symbol"]
            signal = self.analyze_coin(symbol, timeframe)
            if signal and signal.signal_type == "BUY" and signal.strength >= 6:
                signals.append(signal)

        # Remove duplicates và sort by strength
        unique_signals = {}
        for sig in signals:
            if sig.symbol not in unique_signals or sig.strength > unique_signals[sig.symbol].strength:
                unique_signals[sig.symbol] = sig

        final_signals = sorted(unique_signals.values(), key=lambda x: x.strength, reverse=True)

        print(f"\n✅ Found {len(final_signals)} strong signals!")
        return final_signals


def print_signal(signal: TechnicalSignal):
    """In ra tín hiệu đẹp mắt"""
    print(f"\n{'='*60}")
    print(f"🎯 {signal.symbol}")
    print(f"{'='*60}")
    print(f"Signal: {signal.signal_type} | Strength: {signal.strength}/10")
    print(f"Price: ${signal.price:.6f}")
    print(f"Time: {signal.timestamp}")
    print(f"\n📊 Key Indicators:")
    for key, value in signal.indicators.items():
        if value is not None:
            print(f"  • {key}: {value}")
    print(f"\n💡 Reasons:")
    for reason in signal.reasons:
        print(f"  {reason}")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Test
    analyzer = TechnicalAnalyzer(exchange="KUCOIN")

    # Test single coin
    print("Testing single coin analysis...")
    signal = analyzer.analyze_coin("BTCUSDT", "15m")
    if signal:
        print_signal(signal)

    # Test market scan
    print("\nTesting market scan...")
    signals = analyzer.scan_market(timeframe="15m", limit=20)

    print(f"\n🎯 Top Signals:")
    for i, sig in enumerate(signals[:5], 1):
        print(f"\n{i}. {sig.symbol} - {sig.signal_type} ({sig.strength}/10)")
        print(f"   Price: ${sig.price:.6f}")
        print(f"   Top reason: {sig.reasons[0] if sig.reasons else 'N/A'}")
