"""
Risk Management Module

Quản lý rủi ro cho trading system:
- Position sizing
- Stop loss management
- Portfolio risk
- Max drawdown control
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Position:
    """Vị thế giao dịch"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    stop_loss: float
    take_profit: List[float]
    entry_time: str
    strategy: str

    def pnl_percent(self) -> float:
        """Tính % lãi/lỗ"""
        return ((self.current_price - self.entry_price) / self.entry_price) * 100

    def pnl_amount(self, capital: float) -> float:
        """Tính số tiền lãi/lỗ"""
        return (self.pnl_percent() / 100) * capital

    def should_exit(self) -> tuple[bool, str]:
        """Kiểm tra có nên thoát lệnh không"""
        if self.current_price <= self.stop_loss:
            return True, "STOP_LOSS"

        for i, tp in enumerate(self.take_profit):
            if self.current_price >= tp:
                return True, f"TAKE_PROFIT_{i+1}"

        return False, "HOLD"


class RiskManager:
    """Quản lý rủi ro"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.capital = self.config.get("capital", 1000.0)
        self.max_risk_per_trade = self.config.get("max_risk_per_trade", 2.0)  # %
        self.max_positions = self.config.get("max_positions", 3)
        self.max_daily_loss = self.config.get("max_daily_loss", 6.0)  # %
        self.max_drawdown = self.config.get("max_drawdown", 15.0)  # %

        self.positions: List[Position] = []
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.peak_capital = self.capital

    def can_open_position(self) -> tuple[bool, str]:
        """Kiểm tra có thể mở vị thế mới không"""
        # 1. Check max positions
        if len(self.positions) >= self.max_positions:
            return False, f"Max positions reached ({self.max_positions})"

        # 2. Check daily loss limit
        daily_loss_pct = (self.daily_pnl / self.capital) * 100
        if daily_loss_pct <= -self.max_daily_loss:
            return False, f"Daily loss limit reached ({daily_loss_pct:.2f}%)"

        # 3. Check drawdown
        current_drawdown = ((self.peak_capital - self.capital) / self.peak_capital) * 100
        if current_drawdown >= self.max_drawdown:
            return False, f"Max drawdown reached ({current_drawdown:.2f}%)"

        return True, "OK"

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Tính position size dựa trên risk management

        Returns:
            % vốn nên đầu tư
        """
        # Risk per trade
        risk_per_trade = self.capital * (self.max_risk_per_trade / 100)

        # Risk per unit
        risk_per_unit = abs(entry_price - stop_loss)

        if risk_per_unit == 0:
            return 0

        # Position size in currency
        position_size_currency = risk_per_trade / risk_per_unit

        # Position size as % of capital
        position_size_pct = (position_size_currency * entry_price / self.capital) * 100

        # Cap at 10% per position
        return min(position_size_pct, 10.0)

    def add_position(self, position: Position):
        """Thêm vị thế mới"""
        self.positions.append(position)
        print(f"✅ Opened position: {position.symbol} @ ${position.entry_price:.6f}")

    def remove_position(self, symbol: str, exit_price: float, reason: str):
        """Đóng vị thế"""
        position = next((p for p in self.positions if p.symbol == symbol), None)

        if position:
            pnl_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
            pnl_amount = (pnl_pct / 100) * self.capital

            self.daily_pnl += pnl_amount
            self.total_pnl += pnl_amount
            self.capital += pnl_amount

            # Update peak capital
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital

            self.positions.remove(position)

            print(f"❌ Closed position: {symbol} @ ${exit_price:.6f}")
            print(f"   Reason: {reason}")
            print(f"   PNL: {pnl_pct:+.2f}% (${pnl_amount:+.2f})")
            print(f"   New capital: ${self.capital:.2f}")

    def update_position_prices(self, price_updates: Dict[str, float]):
        """Cập nhật giá các vị thế"""
        for position in self.positions:
            if position.symbol in price_updates:
                position.current_price = price_updates[position.symbol]

    def check_exits(self):
        """Kiểm tra các vị thế cần đóng"""
        to_close = []

        for position in self.positions:
            should_exit, reason = position.should_exit()
            if should_exit:
                to_close.append((position.symbol, position.current_price, reason))

        for symbol, price, reason in to_close:
            self.remove_position(symbol, price, reason)

    def get_portfolio_summary(self) -> Dict:
        """Lấy tổng quan portfolio"""
        total_pnl_pct = (self.total_pnl / (self.capital - self.total_pnl)) * 100 if self.capital != self.total_pnl else 0
        current_drawdown = ((self.peak_capital - self.capital) / self.peak_capital) * 100 if self.peak_capital > 0 else 0

        return {
            "capital": round(self.capital, 2),
            "total_pnl": round(self.total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "open_positions": len(self.positions),
            "max_positions": self.max_positions,
            "current_drawdown": round(current_drawdown, 2),
            "max_drawdown": self.max_drawdown,
            "positions": [
                {
                    "symbol": p.symbol,
                    "entry": p.entry_price,
                    "current": p.current_price,
                    "pnl": round(p.pnl_percent(), 2),
                    "strategy": p.strategy
                }
                for p in self.positions
            ]
        }

    def save_state(self, filepath: str = "data/risk_state.json"):
        """Lưu trạng thái"""
        state = {
            "capital": self.capital,
            "total_pnl": self.total_pnl,
            "daily_pnl": self.daily_pnl,
            "peak_capital": self.peak_capital,
            "timestamp": datetime.now().isoformat()
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self, filepath: str = "data/risk_state.json"):
        """Load trạng thái"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                self.capital = state.get("capital", self.capital)
                self.total_pnl = state.get("total_pnl", 0)
                self.daily_pnl = state.get("daily_pnl", 0)
                self.peak_capital = state.get("peak_capital", self.capital)
                print(f"✅ Loaded state from {filepath}")
        except FileNotFoundError:
            print(f"⚠️ No saved state found at {filepath}")


def print_portfolio_summary(summary: Dict):
    """In portfolio summary đẹp mắt"""
    print(f"\n{'='*60}")
    print(f"📊 PORTFOLIO SUMMARY")
    print(f"{'='*60}")
    print(f"Capital: ${summary['capital']:,.2f}")
    print(f"Total PNL: ${summary['total_pnl']:+,.2f} ({summary['total_pnl_pct']:+.2f}%)")
    print(f"Daily PNL: ${summary['daily_pnl']:+,.2f}")
    print(f"\n📍 Positions: {summary['open_positions']}/{summary['max_positions']}")

    if summary['positions']:
        print(f"\nOpen Positions:")
        for pos in summary['positions']:
            print(f"  • {pos['symbol']}: ${pos['current']:.6f} ({pos['pnl']:+.2f}%) - {pos['strategy']}")
    else:
        print("  No open positions")

    print(f"\n⚠️ Risk Metrics:")
    print(f"  Current Drawdown: {summary['current_drawdown']:.2f}%")
    print(f"  Max Drawdown: {summary['max_drawdown']}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test
    print("🧪 Testing Risk Manager\n")

    config = {
        "capital": 1000.0,
        "max_risk_per_trade": 2.0,
        "max_positions": 3,
        "max_daily_loss": 6.0,
        "max_drawdown": 15.0
    }

    rm = RiskManager(config)

    # Test position sizing
    entry = 100.0
    sl = 97.0  # 3% stop loss
    size = rm.calculate_position_size(entry, sl)
    print(f"Position size for entry ${entry}, SL ${sl}: {size:.2f}%")

    # Test can open position
    can_open, msg = rm.can_open_position()
    print(f"\nCan open position? {can_open} - {msg}")

    # Test adding position
    pos = Position(
        symbol="BTCUSDT",
        entry_price=100.0,
        current_price=100.0,
        quantity=1.0,
        stop_loss=97.0,
        take_profit=[103.0, 109.0, 115.0],
        entry_time=datetime.now().isoformat(),
        strategy="Breakout"
    )
    rm.add_position(pos)

    # Update price
    rm.update_position_prices({"BTCUSDT": 105.0})

    # Check portfolio
    summary = rm.get_portfolio_summary()
    print_portfolio_summary(summary)

    # Close position
    rm.remove_position("BTCUSDT", 105.0, "MANUAL")

    # Final summary
    summary = rm.get_portfolio_summary()
    print_portfolio_summary(summary)
