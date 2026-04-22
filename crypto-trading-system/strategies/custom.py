"""
CUSTOM STRATEGY - Template cho chiến lược riêng của bạn

HƯỚng dẫn:
1. Đọc template này
2. Điền logic của bạn vào hàm generate_signal()
3. Test: python strategies/custom.py
4. Sử dụng: ./run.sh --mode trade --strategy custom
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, TradeSignal


class CustomStrategy(BaseStrategy):
    """
    Chiến lược tùy chỉnh của bạn

    VÍ DỤ: RSI Oversold + Volume Spike Strategy

    Điều kiện entry:
    1. RSI < 30 (oversold)
    2. Volume > 3x average
    3. Price trên EMA50
    4. BB không quá rộng
    """

    def __init__(self, config: Dict = None):
        # Cấu hình mặc định
        default_config = {
            "rsi_oversold": 30,          # RSI oversold threshold
            "rsi_overbought": 70,        # RSI overbought threshold
            "volume_multiplier": 3.0,    # Volume phải >3x
            "bbw_max": 0.05,            # BB width tối đa
            "min_change": 2.0,          # Price change tối thiểu (%)
            "risk_reward": 2.5,         # Target R:R
            "position_size": 2.5        # % vốn mỗi lệnh
        }

        if config:
            default_config.update(config)

        super().__init__(name="Custom Strategy", config=default_config)

    def generate_signal(self, coin_data: Dict, timeframe: str = "15m") -> Optional[TradeSignal]:
        """
        Tạo tín hiệu trading từ data

        Args:
            coin_data: Data từ coin_analysis() hoặc TechnicalAnalyzer
            timeframe: Timeframe

        Returns:
            TradeSignal hoặc None
        """
        try:
            # ═══════════════════════════════════════════════════════
            # BƯỚC 1: EXTRACT DATA
            # ═══════════════════════════════════════════════════════

            price_data = coin_data.get("price_data", {})
            bb_analysis = coin_data.get("bollinger_analysis", {})
            technical = coin_data.get("technical_indicators", {})

            # Price info
            current_price = price_data.get("current_price", 0)
            change_percent = price_data.get("change_percent", 0)
            volume = price_data.get("volume", 0)

            # BB info
            bb_rating = bb_analysis.get("rating", 0)
            bbw = bb_analysis.get("bbw", 1.0)
            bb_upper = bb_analysis.get("bb_upper", 0)
            bb_lower = bb_analysis.get("bb_lower", 0)
            bb_middle = bb_analysis.get("bb_middle", 0)

            # Technical indicators
            rsi = technical.get("rsi", 50)
            ema50 = technical.get("ema50", 0)
            ema200 = technical.get("ema200", 0)
            adx = technical.get("adx", 0)
            macd_div = technical.get("macd_divergence", 0)

            symbol = coin_data.get("symbol", "UNKNOWN")

            # Validation
            if not all([current_price, rsi, volume]):
                return None

            # ═══════════════════════════════════════════════════════
            # BƯỚC 2: STRATEGY LOGIC - ĐIỀN LOGIC CỦA BẠN Ở ĐÂY!
            # ═══════════════════════════════════════════════════════

            reasons = []
            confidence = 0
            action = "HOLD"

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 1: RSI Oversold/Overbought               │
            # └─────────────────────────────────────────────────────┘

            if rsi < self.config["rsi_oversold"]:
                # RSI oversold - cơ hội BUY
                action = "BUY"
                confidence += 3
                reasons.append(f"💰 RSI Oversold: {rsi:.1f} - Strong buy opportunity")

            elif rsi > self.config["rsi_overbought"]:
                # RSI overbought - xem xét SELL hoặc skip
                reasons.append(f"⚠️ RSI Overbought: {rsi:.1f} - Risky zone")
                confidence -= 1
                # Bạn có thể thêm SELL logic ở đây

            else:
                # RSI neutral
                if 40 <= rsi <= 60:
                    confidence += 1
                    reasons.append(f"✓ RSI Neutral: {rsi:.1f}")

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 2: Volume Spike                          │
            # └─────────────────────────────────────────────────────┘

            # Ví dụ: Volume >3x average (simplified check)
            if volume > 500000:  # High volume threshold
                confidence += 2
                reasons.append(f"📢 High Volume: {volume:,.0f}")
            elif volume > 100000:
                confidence += 1
                reasons.append(f"✓ Good Volume: {volume:,.0f}")

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 3: Price vs Moving Averages              │
            # └─────────────────────────────────────────────────────┘

            if ema50 and ema200:
                if current_price > ema50 > ema200:
                    # Bullish structure
                    confidence += 2
                    reasons.append(f"🚀 Bullish: Price > EMA50 > EMA200")
                elif current_price > ema50:
                    confidence += 1
                    reasons.append(f"↗️ Price above EMA50")

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 4: Bollinger Band Width                  │
            # └─────────────────────────────────────────────────────┘

            if bbw < self.config["bbw_max"]:
                confidence += 1
                reasons.append(f"✓ BB Width healthy: {bbw:.4f}")
            else:
                reasons.append(f"⚠️ BB too wide: {bbw:.4f} - High volatility")

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 5: Price Change                          │
            # └─────────────────────────────────────────────────────┘

            if abs(change_percent) >= self.config["min_change"]:
                if change_percent > 0:
                    confidence += 1
                    reasons.append(f"📈 Strong momentum: +{change_percent:.2f}%")

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 6: ADX Trend Strength                    │
            # └─────────────────────────────────────────────────────┘

            if adx > 25:
                confidence += 1
                reasons.append(f"💪 Strong trend: ADX {adx:.1f}")

            # ┌─────────────────────────────────────────────────────┐
            # │ ĐIỀU KIỆN 7: MACD (Optional)                       │
            # └─────────────────────────────────────────────────────┘

            if macd_div > 0:
                confidence += 1
                reasons.append(f"📊 MACD Bullish")

            # ═══════════════════════════════════════════════════════
            # BƯỚC 3: QUYẾT ĐỊNH ENTRY
            # ═══════════════════════════════════════════════════════

            # Tùy chỉnh ngưỡng confidence của bạn
            MIN_CONFIDENCE = 5

            if action == "BUY" and confidence >= MIN_CONFIDENCE:
                # Calculate entry parameters
                entry_price = current_price

                # Stop loss calculation
                stop_loss = self.calculate_stop_loss(
                    entry_price=entry_price,
                    bb_lower=bb_lower,
                    method="bollinger"  # hoặc "percentage"
                )

                # Take profit calculation
                take_profit = self.calculate_take_profit(
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    rr_ratio=self.config["risk_reward"]
                )

                # Create signal
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

                # Validate signal
                if self.validate_signal(signal):
                    self.save_signal(signal)
                    return signal

            # No valid signal
            return None

        except Exception as e:
            print(f"Error generating custom signal: {e}")
            return None

    def validate_signal(self, signal: TradeSignal) -> bool:
        """
        Kiểm tra signal có hợp lệ không

        Tùy chỉnh validation rules của bạn ở đây
        """
        # 1. Check R:R ratio
        if signal.risk_reward_ratio() < 1.5:
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

        # Thêm validation rules của bạn ở đây

        return True


# ═══════════════════════════════════════════════════════════════
# TEST SCRIPT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Testing Custom Strategy\n")

    # Import MCP server functions
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tradingview-mcp" / "src"))

    from tradingview_mcp.server import coin_analysis, top_gainers

    # Test với top gainers
    print("1. Finding top gainers...")
    gainers = top_gainers(exchange="KUCOIN", timeframe="15m", limit=5)

    if gainers:
        print(f"Found {len(gainers)} gainers\n")

        strategy = CustomStrategy()

        for coin in gainers[:3]:  # Test first 3
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
        print("No gainers found")
