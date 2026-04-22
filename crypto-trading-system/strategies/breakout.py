"""
Bollinger Band Breakout Strategy

Chiến lược:
1. Tìm coin có BB Width thấp (squeeze)
2. Chờ price breakout khỏi upper/lower band
3. Volume confirmation (>2x average)
4. Entry khi có confirmation
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, TradeSignal


class BreakoutStrategy(BaseStrategy):
    """
    Bollinger Band Breakout Strategy

    Tham số:
    - bbw_threshold: Ngưỡng BBW để xác định squeeze (default: 0.03)
    - volume_multiplier: Volume phải > X lần average (default: 2.0)
    - rsi_range: RSI không quá mua/bán (default: [30, 70])
    - risk_reward: Tỷ lệ R:R tối thiểu (default: 3.0)
    """

    def __init__(self, config: Dict = None):
        default_config = {
            "bbw_threshold": 0.03,
            "volume_multiplier": 2.0,
            "rsi_min": 30,
            "rsi_max": 70,
            "risk_reward": 3.0,
            "position_size": 2.0
        }

        if config:
            default_config.update(config)

        super().__init__(name="Breakout Strategy", config=default_config)

    def generate_signal(self, coin_data: Dict, timeframe: str = "15m") -> Optional[TradeSignal]:
        """
        Tạo tín hiệu breakout

        Args:
            coin_data: Data từ coin_analysis() hoặc TechnicalAnalyzer
            timeframe: Timeframe

        Returns:
            TradeSignal hoặc None
        """
        try:
            # Extract data
            price_data = coin_data.get("price_data", {})
            bb_analysis = coin_data.get("bollinger_analysis", {})
            technical = coin_data.get("technical_indicators", {})

            current_price = price_data.get("current_price", 0)
            change_percent = price_data.get("change_percent", 0)
            volume = price_data.get("volume", 0)

            bb_rating = bb_analysis.get("rating", 0)
            bbw = bb_analysis.get("bbw", 1.0)
            bb_upper = bb_analysis.get("bb_upper", 0)
            bb_lower = bb_analysis.get("bb_lower", 0)
            bb_middle = bb_analysis.get("bb_middle", 0)
            position = bb_analysis.get("position", "")

            rsi = technical.get("rsi", 50)
            adx = technical.get("adx", 0)

            symbol = coin_data.get("symbol", "UNKNOWN")

            # Validation
            if not all([current_price, bb_upper, bb_lower, bbw]):
                return None

            # Strategy Logic
            reasons = []
            confidence = 0
            action = "HOLD"

            # 1. Check for Bollinger Squeeze
            if bbw < self.config["bbw_threshold"]:
                confidence += 2
                reasons.append(f"🔥 BB Squeeze detected (BBW: {bbw:.4f})")

            # 2. Check for Breakout
            if position == "Above Upper":
                # Bullish breakout
                if change_percent > 2.0:  # Price moved up significantly
                    action = "BUY"
                    confidence += 3
                    reasons.append(f"📈 Bullish breakout above upper BB (+{change_percent:.2f}%)")
            elif position == "Below Lower":
                # Bearish signal - could be buy opportunity if oversold
                if rsi < 30 and change_percent < -3.0:
                    action = "BUY"
                    confidence += 2
                    reasons.append(f"💰 Oversold bounce opportunity (RSI: {rsi:.1f})")

            # 3. RSI confirmation
            if self.config["rsi_min"] < rsi < self.config["rsi_max"]:
                confidence += 1
                reasons.append(f"✓ RSI in healthy range: {rsi:.1f}")
            elif rsi > self.config["rsi_max"]:
                reasons.append(f"⚠️ RSI overbought: {rsi:.1f} - Risky entry")
                confidence -= 1

            # 4. Volume confirmation
            if volume > 100000:  # Simple volume check
                confidence += 1
                reasons.append(f"📢 Good volume: {volume:,.0f}")

            # 5. Trend strength
            if adx > 25:
                confidence += 1
                reasons.append(f"💪 Strong trend (ADX: {adx:.1f})")

            # 6. BB Rating confirmation
            if bb_rating >= 2:
                confidence += 2
                reasons.append(f"🎯 Strong BB rating: +{bb_rating}")
            elif bb_rating >= 1:
                confidence += 1
                reasons.append(f"↗️ Positive BB rating: +{bb_rating}")

            # Decision
            if action == "BUY" and confidence >= 5:
                # Calculate entry parameters
                entry_price = current_price
                stop_loss = self.calculate_stop_loss(
                    entry_price=entry_price,
                    bb_lower=bb_lower,
                    method="bollinger"
                )

                take_profit = self.calculate_take_profit(
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    rr_ratio=self.config["risk_reward"]
                )

                signal = TradeSignal(
                    symbol=symbol,
                    action=action,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.config["position_size"],
                    confidence=min(confidence, 10),
                    strategy_name=self.name,
                    reasons=reasons,
                    timestamp=datetime.now().isoformat(),
                    timeframe=timeframe
                )

                if self.validate_signal(signal):
                    self.save_signal(signal)
                    return signal

            return None

        except Exception as e:
            print(f"Error generating breakout signal: {e}")
            return None

    def validate_signal(self, signal: TradeSignal) -> bool:
        """Kiểm tra signal hợp lệ"""
        # 1. Check R:R ratio
        if signal.risk_reward_ratio() < 2.0:
            print(f"❌ Poor R:R ratio: {signal.risk_reward_ratio():.2f}")
            return False

        # 2. Check risk percentage
        if signal.risk_percentage() > 5.0:
            print(f"❌ Risk too high: {signal.risk_percentage():.2f}%")
            return False

        # 3. Check confidence
        if signal.confidence < 5:
            print(f"❌ Low confidence: {signal.confidence}/10")
            return False

        return True


if __name__ == "__main__":
    # Test strategy
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tradingview-mcp" / "src"))

    from tradingview_mcp.server import coin_analysis, bollinger_scan

    print("🧪 Testing Breakout Strategy\n")

    # Test with bollinger scan
    print("1. Scanning for squeeze coins...")
    squeeze_coins = bollinger_scan(
        exchange="KUCOIN",
        timeframe="15m",
        bbw_threshold=0.03,
        limit=10
    )

    if squeeze_coins:
        print(f"Found {len(squeeze_coins)} coins with BB squeeze\n")

        strategy = BreakoutStrategy()

        for coin in squeeze_coins[:3]:  # Test first 3
            symbol = coin["symbol"].split(":")[1] if ":" in coin["symbol"] else coin["symbol"]
            print(f"\n{'='*60}")
            print(f"Analyzing {symbol}...")

            # Get detailed analysis
            data = coin_analysis(symbol=symbol, exchange="KUCOIN", timeframe="15m")

            if "error" not in data:
                signal = strategy.generate_signal(data, timeframe="15m")

                if signal:
                    from strategies.base_strategy import print_trade_signal
                    print_trade_signal(signal)
                else:
                    print(f"No signal generated for {symbol}")
            else:
                print(f"Error: {data['error']}")

        # Print stats
        print(f"\n{'='*60}")
        print("Strategy Statistics:")
        stats = strategy.get_signal_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("No squeeze coins found")
