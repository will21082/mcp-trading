# 📖 Hướng dẫn sử dụng Trading System

## 🎯 Cách chạy hệ thống

### Option 1: Sử dụng script (Khuyến nghị)

```bash
cd crypto-trading-system

# Quét thị trường
./run.sh --mode scan --timeframe 15m

# Tạo trade signals
./run.sh --mode trade --strategy breakout --timeframe 15m

# Xem portfolio
./run.sh --mode portfolio
```

### Option 2: Chạy trực tiếp

```bash
cd tradingview-mcp
uv run python ../crypto-trading-system/main.py --mode scan --timeframe 15m
```

## 📊 Các chế độ hoạt động

### 1. SCAN - Quét thị trường

**Mục đích**: Tìm cơ hội trading

```bash
./run.sh --mode scan --timeframe 15m --limit 20
```

**Kết quả**:
- Danh sách coins có tín hiệu mạnh
- Điểm confidence (1-10)
- Lý do (reasons) tại sao nên quan tâm
- Lưu vào `data/signals_15m.json`

**Khi nào dùng**:
- Hàng ngày để tìm cơ hội
- Khi muốn overview thị trường
- Để build watchlist

### 2. TRADE - Tạo tín hiệu giao dịch

**Mục đích**: Tạo entry/exit plans chi tiết

```bash
./run.sh --mode trade --strategy breakout --timeframe 15m
```

**Kết quả**:
- Trade signals với Entry, Stop Loss, Take Profit
- Risk/Reward ratio
- Position sizing
- Confidence score
- Hỏi bạn có muốn "execute" (simulation)

**Khi nào dùng**:
- Khi đã tìm được coin từ SCAN mode
- Khi muốn entry plan cụ thể
- Để backtest chiến lược

### 3. PORTFOLIO - Xem trạng thái

**Mục đích**: Theo dõi portfolio

```bash
./run.sh --mode portfolio
```

**Kết quả**:
- Vốn hiện tại
- PNL (lãi/lỗ)
- Các vị thế đang mở
- Risk metrics (drawdown, etc.)

**Khi nào dùng**:
- Hàng ngày để review
- Sau khi "execute" signals
- Để tracking performance

## 🎮 Workflow thực tế

### Buổi sáng (Setup)

```bash
# 1. Quét thị trường 4h (big picture)
./run.sh --mode scan --timeframe 4h --limit 30

# 2. Quét thị trường 1h
./run.sh --mode scan --timeframe 1h --limit 20
```

→ Tìm coins có tiềm năng, thêm vào watchlist

### Buổi chiều (Entry)

```bash
# 1. Tạo trade signals cho watchlist
./run.sh --mode trade --strategy breakout --timeframe 15m

# 2. Review signals
# → Đọc kỹ entry, SL, TP
# → Check chart trên TradingView để confirm
# → Quyết định có vào lệnh không
```

### Buổi tối (Review)

```bash
# Xem portfolio
./run.sh --mode portfolio

# → Check các lệnh đã vào
# → Update stop loss nếu cần
# → Take profit nếu đạt target
```

## 🎯 Ví dụ cụ thể

### Ví dụ 1: Tìm Breakout cơ hội

```bash
./run.sh --mode scan --timeframe 15m --limit 20
```

**Output mẫu**:
```
✅ Found 12 strong signals!

1. KUCOIN:NAYMUSDT - BUY (10/10)
   Price: $0.001300
   📈 Bollinger Rating: +2 (Strong Buy)

2. KUCOIN:ISPUSDT - BUY (10/10)
   Price: $0.000200
   🔥 BB Squeeze detected (BBW: 0.0234)
```

**Bước tiếp theo**:
1. Vào TradingView.com
2. Tìm coin: KUCOIN:NAYMUSDT
3. Xem chart 15m confirm BB pattern
4. Nếu OK → Chạy trade mode

### Ví dụ 2: Vào lệnh

```bash
./run.sh --mode trade --strategy breakout --timeframe 15m
```

**Output mẫu**:
```
🎯 TRADE SIGNAL - Breakout Strategy
Symbol: KUCOIN:NAYMUSDT
Action: BUY | Confidence: 8/10

Entry Price: $0.001300
Stop Loss:   $0.001261 (3.00%)
Take Profit:
  TP1: $0.001358 (+4.46%)
  TP2: $0.001417 (+9.00%)
  TP3: $0.001475 (+13.46%)

Position Size: 2.0% of capital
Risk/Reward: 1:3.00

Execute this signal? (y/n):
```

**Nếu y → "Execute" (simulation)**:
- Hệ thống ghi nhận position
- Lưu vào portfolio
- Bạn tự vào lệnh thật trên exchange

**Nếu n → Skip**

### Ví dụ 3: Quản lý portfolio

```bash
./run.sh --mode portfolio
```

**Output mẫu**:
```
📊 PORTFOLIO SUMMARY
Capital: $1,000.00
Total PNL: $+50.00 (+5.00%)
Daily PNL: $+20.00

📍 Positions: 2/3

Open Positions:
  • KUCOIN:NAYMUSDT: $0.001350 (+3.85%) - Breakout
  • KUCOIN:BTCUSDT: $45,200 (+1.20%) - Breakout

⚠️ Risk Metrics:
  Current Drawdown: 0.00%
  Max Drawdown: 15%
```

## ⚙️ Tùy chỉnh chiến lược

### Điều chỉnh config

File: `config/settings.json`

```json
{
  "exchange": "KUCOIN",           // ← Đổi exchange

  "breakout_config": {
    "bbw_threshold": 0.03,        // ← BB squeeze threshold
    "volume_multiplier": 2.0,     // ← Volume tối thiểu
    "risk_reward": 3.0,           // ← Target R:R
    "rsi_min": 30,                // ← RSI range
    "rsi_max": 70
  },

  "risk_config": {
    "max_risk_per_trade": 2.0,    // ← Risk % mỗi lệnh
    "max_positions": 3,           // ← Số lệnh tối đa
    "max_daily_loss": 6.0,        // ← Stop khi lỗ %
    "max_drawdown": 15.0          // ← Max drawdown
  }
}
```

### Tạo watchlist riêng

File: `data/watchlist.json`

```json
{
  "watchlist": [
    "BTCUSDT",
    "ETHUSDT",
    "YOURCOINSHERE"
  ]
}
```

## 🛡️ Risk Management Rules

### Quy tắc vàng:

1. **Position Size**: Không bao giờ >5% vốn
2. **Stop Loss**: Luôn luôn set SL
3. **Risk/Reward**: Tối thiểu 1:2, target 1:3
4. **Max Positions**: Không quá 3-5 lệnh cùng lúc
5. **Daily Loss Limit**: Stop khi lỗ 6% trong ngày
6. **Max Drawdown**: Stop trading khi drawdown >15%

### Checklist trước khi vào lệnh:

- [ ] Confidence ≥ 7/10?
- [ ] R:R ≥ 1:2?
- [ ] Position size ≤ 3%?
- [ ] SL được set?
- [ ] Confirm trên chart?
- [ ] Volume đủ lớn?

## 📝 Tips quan trọng

### 1. Timeframe selection

- **5m-15m**: Scalping (cần theo dõi liên tục)
- **1h**: Swing trading (check 2-3 lần/ngày)
- **4h-1D**: Position trading (check 1 lần/ngày)

### 2. Confidence scoring

- **8-10**: Tín hiệu rất mạnh, có thể vào ngay
- **6-7**: Tín hiệu tốt, cần confirm thêm
- **<6**: Skip, tín hiệu yếu

### 3. Multiple timeframe

Luôn confirm trên nhiều timeframes:
```bash
# Check 15m
./run.sh --mode scan --timeframe 15m

# Confirm với 1h
./run.sh --mode scan --timeframe 1h
```

Nếu cả 2 đều có signal → Mạnh hơn!

### 4. Volume là vua

Ưu tiên coins có:
- Volume >100k
- Volume spike >2x average
- Volume tăng khi breakout

### 5. Không all-in

❌ **ĐỪNG BAO GIỜ**:
- All-in vào 1 coin
- Không set stop loss
- Revenge trading sau khi lỗ
- FOMO vào khi đã breakout xa

✅ **NÊN**:
- Chia nhỏ vốn
- Luôn có exit plan
- Chấp nhận loss nhỏ
- Chờ đợi setup tốt

## 🐛 Troubleshooting

### "No signals found"

→ Thử:
- Đổi timeframe khác
- Tăng limit (--limit 50)
- Đổi exchange (sửa config)

### "Module not found"

→ Chạy từ tradingview-mcp với uv:
```bash
cd tradingview-mcp
uv run python ../crypto-trading-system/main.py ...
```

### Signals không chính xác?

→ Điều chỉnh config:
- Giảm bbw_threshold
- Tăng volume_multiplier
- Điều chỉnh RSI range

## 📚 Học thêm

1. **Bollinger Bands**: https://tradingview.com/wiki/Bollinger_Bands
2. **RSI**: https://tradingview.com/wiki/Relative_Strength_Index
3. **Volume Analysis**: Đọc trong README.md
4. **Risk Management**: Quan trọng nhất!

---

**Remember**: Đây là công cụ hỗ trợ, KHÔNG phải thánh grail. Luôn tự nghiên cứu và quản lý rủi ro!

🚀 Happy Trading!
