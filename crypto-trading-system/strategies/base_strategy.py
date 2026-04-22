"""
Base class cho tất cả trading strategies
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class TradeSignal:
    """Tín hiệu giao dịch"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    entry_price: float
    stop_loss: float
    take_profit: List[float]  # Multiple TP levels
    position_size: float  # % of capital
    confidence: int  # 1-10
    strategy_name: str
    reasons: List[str]
    timestamp: str
    timeframe: str

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "action": self.action,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "position_size": self.position_size,
            "confidence": self.confidence,
            "strategy_name": self.strategy_name,
            "reasons": self.reasons,
            "timestamp": self.timestamp,
            "timeframe": self.timeframe
        }

    def risk_reward_ratio(self) -> float:
        """Tính tỷ lệ Risk/Reward"""
        if not self.take_profit or self.stop_loss >= self.entry_price:
            return 0

        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit[0] - self.entry_price)

        if risk == 0:
            return 0
        return reward / risk

    def risk_percentage(self) -> float:
        """Tính % rủi ro của lệnh"""
        if self.entry_price == 0:
            return 0
        return abs((self.stop_loss - self.entry_price) / self.entry_price) * 100


class BaseStrategy(ABC):
    """Base class cho tất cả strategies"""

    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        self.signals_history = []

    @abstractmethod
    def generate_signal(self, coin_data: Dict, timeframe: str = "15m") -> Optional[TradeSignal]:
        """
        Tạo tín hiệu giao dịch từ dữ liệu coin

        Args:
            coin_data: Dữ liệu phân tích từ TechnicalAnalyzer
            timeframe: Khung thời gian

        Returns:
            TradeSignal hoặc None
        """
        pass

    @abstractmethod
    def validate_signal(self, signal: TradeSignal) -> bool:
        """
        Kiểm tra tín hiệu có hợp lệ không

        Args:
            signal: TradeSignal cần kiểm tra

        Returns:
            True nếu hợp lệ
        """
        pass

    def calculate_position_size(self, capital: float, risk_percent: float = 2.0) -> float:
        """
        Tính position size dựa trên vốn và % risk

        Args:
            capital: Tổng vốn
            risk_percent: % vốn sẵn sàng risk

        Returns:
            Position size (% of capital)
        """
        return min(risk_percent, 5.0)  # Max 5% mỗi lệnh

    def calculate_stop_loss(self, entry_price: float, atr: float = None,
                           bb_lower: float = None, method: str = "percentage") -> float:
        """
        Tính stop loss

        Args:
            entry_price: Giá vào lệnh
            atr: Average True Range (nếu có)
            bb_lower: Bollinger Band Lower (nếu có)
            method: "percentage", "atr", "bollinger"

        Returns:
            Stop loss price
        """
        if method == "percentage":
            return entry_price * 0.97  # 3% stop loss
        elif method == "atr" and atr:
            return entry_price - (2 * atr)
        elif method == "bollinger" and bb_lower:
            return bb_lower * 0.99
        else:
            return entry_price * 0.97

    def calculate_take_profit(self, entry_price: float, stop_loss: float,
                             rr_ratio: float = 3.0) -> List[float]:
        """
        Tính take profit levels

        Args:
            entry_price: Giá vào lệnh
            stop_loss: Stop loss price
            rr_ratio: Risk/Reward ratio

        Returns:
            List of TP levels
        """
        risk = abs(entry_price - stop_loss)

        # Multiple TP levels
        tp1 = entry_price + (risk * rr_ratio * 0.5)  # 50% at 1.5R
        tp2 = entry_price + (risk * rr_ratio)         # 30% at 3R
        tp3 = entry_price + (risk * rr_ratio * 1.5)   # 20% at 4.5R

        return [tp1, tp2, tp3]

    def save_signal(self, signal: TradeSignal):
        """Lưu signal vào history"""
        self.signals_history.append(signal)

    def get_signal_stats(self) -> Dict:
        """Lấy thống kê signals"""
        if not self.signals_history:
            return {"total": 0}

        buy_signals = [s for s in self.signals_history if s.action == "BUY"]
        sell_signals = [s for s in self.signals_history if s.action == "SELL"]

        avg_confidence = sum(s.confidence for s in self.signals_history) / len(self.signals_history)
        avg_rr = sum(s.risk_reward_ratio() for s in self.signals_history) / len(self.signals_history)

        return {
            "total": len(self.signals_history),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "avg_confidence": round(avg_confidence, 2),
            "avg_risk_reward": round(avg_rr, 2)
        }


def print_trade_signal(signal: TradeSignal):
    """In trade signal đẹp mắt"""
    print(f"\n{'='*70}")
    print(f"🎯 TRADE SIGNAL - {signal.strategy_name}")
    print(f"{'='*70}")
    print(f"Symbol: {signal.symbol}")
    print(f"Action: {signal.action} | Confidence: {signal.confidence}/10")
    print(f"Timeframe: {signal.timeframe}")
    print(f"\n💰 Entry Details:")
    print(f"  Entry Price: ${signal.entry_price:.6f}")
    print(f"  Stop Loss:   ${signal.stop_loss:.6f} ({signal.risk_percentage():.2f}%)")
    print(f"  Take Profit:")
    for i, tp in enumerate(signal.take_profit, 1):
        profit_pct = ((tp - signal.entry_price) / signal.entry_price) * 100
        print(f"    TP{i}: ${tp:.6f} (+{profit_pct:.2f}%)")
    print(f"\n📊 Risk Management:")
    print(f"  Position Size: {signal.position_size:.1f}% of capital")
    print(f"  Risk/Reward: 1:{signal.risk_reward_ratio():.2f}")
    print(f"\n💡 Reasons:")
    for reason in signal.reasons:
        print(f"  • {reason}")
    print(f"\n⏰ Time: {signal.timestamp}")
    print(f"{'='*70}\n")
