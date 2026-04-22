# 🚀 Crypto Trading System

Hệ thống phân tích và trading tự động cho cryptocurrency sử dụng TradingView MCP Server.

## 📁 Cấu trúc Project

```
crypto-trading-system/
├── analyzers/           # Các module phân tích kỹ thuật
│   ├── technical.py     # Phân tích technical indicators
│   ├── volume.py        # Phân tích volume
│   ├── pattern.py       # Nhận diện pattern
│   └── scanner.py       # Quét thị trường
│
├── strategies/          # Các chiến lược trading
│   ├── base_strategy.py # Base class cho strategies
│   ├── breakout.py      # Chiến lược breakout
│   ├── scalping.py      # Chiến lược scalping
│   ├── swing.py         # Chiến lược swing trading
│   └── custom.py        # Chiến lược tùy chỉnh của bạn
│
├── data/               # Dữ liệu và database
│   ├── watchlist.json  # Danh sách coin theo dõi
│   ├── signals.json    # Lịch sử tín hiệu
│   └── trades.json     # Lịch sử giao dịch
│
├── logs/               # Log files
│   └── trading.log     # Log giao dịch
│
├── backtests/          # Kết quả backtest
│   └── results/        # Kết quả chi tiết
│
├── config/             # File cấu hình
│   ├── settings.json   # Cấu hình chung
│   └── exchanges.json  # Cấu hình exchanges
│
├── main.py            # File chính chạy bot
├── trader.py          # Module thực thi lệnh
├── risk_manager.py    # Quản lý rủi ro
├── dashboard.py       # Dashboard theo dõi
└── requirements.txt   # Dependencies

```

## 🎯 Tính năng chính

### 1. Phân tích Kỹ thuật
- ✅ Technical Indicators (RSI, MACD, Bollinger Bands)
- ✅ Volume Analysis
- ✅ Pattern Recognition (Candlestick patterns)
- ✅ Multi-timeframe Analysis

### 2. Chiến lược Trading
- ✅ Breakout Strategy (Đột phá Bollinger Bands)
- ✅ Scalping (Giao dịch ngắn hạn)
- ✅ Swing Trading (Giao dịch trung hạn)
- ✅ Custom Strategy (Tự tạo chiến lược)

### 3. Quản lý Rủi ro
- ✅ Position Sizing
- ✅ Stop Loss / Take Profit
- ✅ Risk/Reward Ratio
- ✅ Max Drawdown Control

### 4. Tính năng khác
- ✅ Real-time Scanning
- ✅ Signal Notifications
- ✅ Performance Tracking
- ✅ Backtest System

## 🚀 Cài đặt

```bash
cd crypto-trading-system
pip install -r requirements.txt
```

## ⚙️ Cấu hình

1. Chỉnh sửa `config/settings.json`:
```json
{
  "exchange": "KUCOIN",
  "timeframes": ["15m", "1h", "4h"],
  "risk_per_trade": 2.0,
  "max_positions": 3
}
```

2. Thêm watchlist vào `data/watchlist.json`

## 🎮 Sử dụng

### Quét thị trường
```bash
python main.py --mode scan
```

### Chạy chiến lược
```bash
python main.py --mode trade --strategy breakout
```

### Xem dashboard
```bash
python dashboard.py
```

### Backtest
```bash
python main.py --mode backtest --strategy breakout --days 30
```

## 📊 Chiến lược mẫu

### 1. Breakout Strategy
- Tìm coin có Bollinger Band Width thấp (squeeze)
- Chờ breakout khỏi upper/lower band
- Volume confirmation (>2x average)
- Entry khi có confirmation

### 2. Volume Spike Strategy
- Quét coin có volume tăng đột biến (>3x)
- Kiểm tra RSI không quá mua/bán
- Entry theo hướng momentum
- Quick profit taking

### 3. Scalping Strategy
- Timeframe: 5m, 15m
- RSI extremes (>70 hoặc <30)
- Quick entries/exits
- Tight stop loss (1-2%)

## 🛡️ Risk Management

- **Position Size**: 1-3% vốn mỗi lệnh
- **Stop Loss**: 1-3% mỗi lệnh
- **Take Profit**: 3-9% (Risk:Reward 1:3)
- **Max Positions**: 3-5 lệnh cùng lúc
- **Max Daily Loss**: 6% vốn

## 📈 Theo dõi Performance

```bash
python dashboard.py --report daily
python dashboard.py --report weekly
```

## ⚠️ Lưu ý quan trọng

1. Đây là hệ thống phân tích và đề xuất, KHÔNG tự động trade
2. Luôn kiểm tra signals trước khi vào lệnh
3. Backtest kỹ trước khi dùng thật
4. Quản lý vốn chặt chẽ
5. KHÔNG all-in vào một lệnh

## 🔧 Tùy chỉnh

Tạo chiến lược riêng trong `strategies/custom.py`:

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def analyze(self, coin_data):
        # Logic của bạn
        return signal
```

## 📞 Hỗ trợ

- Xem logs: `logs/trading.log`
- Kiểm tra signals: `data/signals.json`
- Review trades: `data/trades.json`

---

**Lưu ý**: Hệ thống này sử dụng TradingView MCP Server để lấy dữ liệu miễn phí. Không cần API key từ exchanges để phân tích, chỉ cần khi muốn thực thi lệnh thật.
