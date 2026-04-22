# 🚀 Quick Start Guide

Hướng dẫn nhanh sử dụng Crypto Trading System

## 📋 Cài đặt

```bash
cd crypto-trading-system

# Không cần cài thêm gì, sử dụng luôn TradingView MCP đã có
# Hoặc nếu muốn chạy độc lập:
# pip install -r requirements.txt
```

## 🎯 Sử dụng cơ bản

### 1. Quét thị trường (Market Scan)

Tìm cơ hội trading:

```bash
# Quét KuCoin với timeframe 15m
python main.py --mode scan --timeframe 15m --limit 20

# Quét với timeframe 1h
python main.py --mode scan --timeframe 1h --limit 30
```

**Output**: Danh sách các coin có tín hiệu mạnh, kèm lý do

### 2. Tạo tín hiệu Trading (Trade Signals)

Tạo tín hiệu chi tiết với entry/stop loss/take profit:

```bash
# Sử dụng Breakout strategy
python main.py --mode trade --strategy breakout --timeframe 15m

# Tự động thực thi (không cần confirm)
python main.py --mode trade --strategy breakout --timeframe 15m --auto
```

**Output**: Trade signals với đầy đủ thông tin entry, SL, TP, R:R ratio

### 3. Xem Portfolio

Xem tình trạng portfolio hiện tại:

```bash
python main.py --mode portfolio
```

## 📊 Ví dụ thực tế

### Scenario 1: Tìm Breakout trong 15 phút

```bash
python main.py --mode scan --timeframe 15m --limit 30
```

Hệ thống sẽ:
1. Quét top gainers trên KuCoin
2. Tìm coins có BB squeeze (BBW < 0.03)
3. Tìm volume breakouts (>2x volume)
4. Phân tích và cho điểm từng coin
5. Trả về top signals

### Scenario 2: Vào lệnh với Breakout Strategy

```bash
python main.py --mode trade --strategy breakout --timeframe 15m
```

Hệ thống sẽ:
1. Quét thị trường tìm cơ hội
2. Áp dụng Breakout strategy logic:
   - BB squeeze detected
   - Price breakout confirmation
   - Volume spike
   - RSI healthy range
3. Tính entry price, stop loss, take profit
4. Hiển thị trade signals
5. Hỏi bạn có muốn execute không

### Scenario 3: Theo dõi Portfolio

```bash
python main.py --mode portfolio
```

Hiển thị:
- Vốn hiện tại
- PNL (Profit & Loss)
- Các vị thế đang mở
- Risk metrics

## ⚙️ Tùy chỉnh cấu hình

Chỉnh sửa `config/settings.json`:

```json
{
  "exchange": "KUCOIN",          // Đổi exchange
  "timeframes": ["15m", "1h"],   // Timeframes ưa thích
  "capital": 1000.0,             // Vốn ban đầu

  "risk_config": {
    "max_risk_per_trade": 2.0,   // Risk 2% mỗi lệnh
    "max_positions": 3,           // Tối đa 3 lệnh cùng lúc
    "max_daily_loss": 6.0,        // Dừng nếu lỗ 6% trong ngày
    "max_drawdown": 15.0          // Dừng nếu drawdown >15%
  },

  "breakout_config": {
    "bbw_threshold": 0.03,        // BB squeeze threshold
    "volume_multiplier": 2.0,     // Volume phải >2x
    "risk_reward": 3.0            // Target R:R 1:3
  }
}
```

## 🎓 Hiểu về Breakout Strategy

### Điều kiện Entry (BUY):

1. **BB Squeeze** (BBW < 0.03)
   - Bollinger Bands thu hẹp
   - Báo hiệu breakout sắp xảy ra

2. **Price Breakout**
   - Giá vượt upper BB
   - Hoặc giá dưới lower BB + RSI oversold (<30)

3. **Volume Confirmation**
   - Volume tăng đột biến
   - Xác nhận sức mạnh của breakout

4. **RSI Healthy** (30-70)
   - Không quá mua/bán
   - Còn room để chạy

5. **Trend Strength** (ADX > 25)
   - Trend đủ mạnh

### Risk Management:

- **Stop Loss**: Dưới lower BB hoặc 3% từ entry
- **Take Profit**: Multiple levels (1.5R, 3R, 4.5R)
- **Position Size**: 2% vốn (có thể tăng nếu signal mạnh)
- **Risk/Reward**: Tối thiểu 1:2, target 1:3

## 📝 Workflow khuyến nghị

### Hàng ngày:

1. **Sáng** (8-9h):
   ```bash
   # Quét thị trường timeframe lớn
   python main.py --mode scan --timeframe 4h
   ```

2. **Trưa** (12-13h):
   ```bash
   # Quét timeframe trung bình
   python main.py --mode scan --timeframe 1h
   ```

3. **Chiều** (16-18h):
   ```bash
   # Tìm trade signals
   python main.py --mode trade --strategy breakout --timeframe 15m
   ```

4. **Tối** (21-22h):
   ```bash
   # Review portfolio
   python main.py --mode portfolio
   ```

### Mỗi lệnh:

1. **Phân tích signal** - Đọc kỹ reasons
2. **Kiểm tra chart** - Confirm bằng mắt trên TradingView
3. **Check risk** - R:R ratio ít nhất 1:2
4. **Execute** - Vào lệnh với đúng position size
5. **Set SL/TP** - Ngay sau khi vào lệnh
6. **Monitor** - Theo dõi và điều chỉnh nếu cần

## 🔍 Debug & Logs

- **Signals**: `data/signals_*.json`
- **Trade signals**: `data/trade_signals_*.json`
- **Risk state**: `data/risk_state.json`
- **Logs**: `logs/trading.log` (nếu có)

## ⚠️ Lưu ý quan trọng

1. **PAPER TRADING**: Hệ thống này chỉ tạo signals, KHÔNG tự động trade
2. **Backtest trước**: Test chiến lược trước khi dùng tiền thật
3. **Risk management**: LUÔN tuân thủ stop loss
4. **Không all-in**: Không bao giờ đầu tư >5% vốn vào 1 lệnh
5. **Tâm lý**: Không revenge trading khi thua lỗ

## 💡 Tips

- **Best timeframes**: 15m cho scalping, 1h cho swing
- **Best exchange**: KuCoin có data ổn định nhất
- **Confidence threshold**: Chỉ vào lệnh khi confidence ≥ 7/10
- **Volume**: Ưu tiên coins có volume >100k
- **Multiple TF**: Confirm signal trên nhiều timeframes

## 📞 Cần giúp đỡ?

Xem file README.md chính để biết thêm chi tiết!
