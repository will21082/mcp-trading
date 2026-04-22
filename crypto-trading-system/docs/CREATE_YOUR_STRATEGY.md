# 🎨 Tạo Chiến Lược Trading Riêng

## 🎯 Hướng dẫn từng bước

### **BƯỚC 1: Hiểu về chiến lược hiện tại**

Đọc file: `STRATEGY_EXPLAINED.md` để hiểu:
- Breakout Strategy hoạt động như thế nào
- Các indicators được sử dụng
- Logic scoring system

### **BƯỚC 2: Ý tưởng chiến lược của bạn**

Trả lời các câu hỏi:

#### **1. Entry Conditions - Khi nào vào lệnh?**

Ví dụ:
- RSI < 30 (oversold)
- Volume >3x average
- Price vượt SMA20
- MACD cross bullish
- Support/Resistance breakout

**Chiến lược của bạn:**
```
□ Điều kiện 1: ________________________________
□ Điều kiện 2: ________________________________
□ Điều kiện 3: ________________________________
□ Điều kiện 4: ________________________________
```

#### **2. Exit Strategy - Khi nào thoát lệnh?**

**Stop Loss:**
- Phần trăm cố định (VD: 3%)
- Dựa vào BB Lower
- ATR-based
- Support level

**Take Profit:**
- Target cố định (VD: 6%)
- Multiple levels (3%, 6%, 9%)
- Trailing stop
- Resistance levels

**Chiến lược của bạn:**
```
Stop Loss: ____________________________________
Take Profit: ___________________________________
```

#### **3. Risk/Reward - Tỷ lệ mục tiêu?**

```
Risk/Reward ratio: 1:_____ (khuyến nghị: 1:2 đến 1:3)
Position size: _____% (khuyến nghị: 2-3%)
```

#### **4. Timeframe - Khung thời gian nào?**

```
□ 5m-15m: Scalping (ngắn hạn)
□ 1h-4h: Swing trading (trung hạn)
□ 1D+: Position trading (dài hạn)
```

---

## 💻 BƯỚC 3: Code chiến lược

### **Cách 1: Sửa file `strategies/custom.py`**

File template đã có sẵn với comments hướng dẫn:

```python
# ═══════════════════════════════════════════════════════
# ĐIỀN LOGIC CỦA BẠN Ở ĐÂY!
# ═══════════════════════════════════════════════════════

# ĐIỀU KIỆN 1: RSI Check
if rsi < 30:
    action = "BUY"
    confidence += 3
    reasons.append("RSI Oversold")

# ĐIỀU KIỆN 2: Volume Check
if volume > 500000:
    confidence += 2
    reasons.append("High Volume")

# ... thêm điều kiện của bạn
```

### **Cách 2: Tạo file mới** (Advanced)

```bash
cd strategies
cp custom.py my_strategy.py
```

Sửa class name:
```python
class MyStrategy(BaseStrategy):
    def __init__(self, config: Dict = None):
        default_config = {
            # Config của bạn
        }
        super().__init__(name="My Strategy", config=default_config)
```

---

## 🧪 BƯỚC 4: Test chiến lược

### **Test 1: Run file trực tiếp**

```bash
cd tradingview-mcp
uv run python ../crypto-trading-system/strategies/custom.py
```

Sẽ test với top gainers và in ra signals.

### **Test 2: Integrate vào main system**

Sửa `main.py`:

```python
from strategies.custom import CustomStrategy

# Trong __init__:
self.strategies = {
    "breakout": BreakoutStrategy(...),
    "custom": CustomStrategy(...)  # ← Thêm dòng này
}
```

Chạy:
```bash
./run.sh --mode trade --strategy custom --timeframe 15m
```

---

## 📋 VÍ DỤ: 3 Chiến lược cụ thể

### **Chiến lược 1: RSI Mean Reversion**

**Concept:** Mua khi oversold, bán khi overbought

**Entry:**
```python
# BUY when:
if rsi < 25:              # Deep oversold
    if volume > avg * 2:  # Volume confirmation
        if price > ema50: # Still in uptrend
            → BUY
```

**Exit:**
```python
Stop Loss: 2% hoặc dưới recent low
Take Profit: RSI reaches 50-60
```

**Code snippet:**
```python
if rsi < 25 and volume > 200000 and current_price > ema50:
    action = "BUY"
    confidence += 4
    reasons.append(f"Deep oversold RSI: {rsi}")
```

---

### **Chiến lược 2: EMA Crossover**

**Concept:** Follow trend khi EMA cross

**Entry:**
```python
# BUY when:
if ema50 > ema200:           # Golden cross
    if current_price > ema50: # Price confirms
        if adx > 25:          # Strong trend
            → BUY
```

**Exit:**
```python
Stop Loss: Dưới EMA50
Take Profit: R:R 1:3
```

**Code snippet:**
```python
if ema50 and ema200 and ema50 > ema200:
    if current_price > ema50:
        if adx > 25:
            action = "BUY"
            confidence += 5
            reasons.append("Golden Cross + Price confirmation")
```

---

### **Chiến lược 3: Volume Breakout**

**Concept:** Volume spike = big move incoming

**Entry:**
```python
# BUY when:
if volume > avg_volume * 5:    # Huge volume spike
    if change_percent > 3:      # Strong price move
        if rsi < 70:            # Not overbought yet
            → BUY
```

**Exit:**
```python
Stop Loss: 3%
Take Profit: 9% (1:3 R:R)
```

**Code snippet:**
```python
# Simplified volume check
if volume > 1000000:  # Very high volume
    if change_percent > 3 and rsi < 70:
        action = "BUY"
        confidence += 5
        reasons.append(f"Volume breakout: {volume:,.0f}")
```

---

## 🎓 INDICATORS AVAILABLE

Bạn có thể sử dụng các indicators này:

### **Price Data:**
```python
current_price = price_data.get("current_price", 0)
change_percent = price_data.get("change_percent", 0)
volume = price_data.get("volume", 0)
open_price = price_data.get("open")
high = price_data.get("high")
low = price_data.get("low")
```

### **Bollinger Bands:**
```python
bb_rating = bb_analysis.get("rating", 0)        # -3 to +3
bbw = bb_analysis.get("bbw", 1.0)              # Width
bb_upper = bb_analysis.get("bb_upper", 0)
bb_lower = bb_analysis.get("bb_lower", 0)
bb_middle = bb_analysis.get("bb_middle", 0)
bb_position = bb_analysis.get("position", "")  # Above/Below/Within
```

### **Technical Indicators:**
```python
rsi = technical.get("rsi", 50)
sma20 = technical.get("sma20", 0)
ema50 = technical.get("ema50", 0)
ema200 = technical.get("ema200", 0)
adx = technical.get("adx", 0)
macd = technical.get("macd", 0)
macd_signal = technical.get("macd_signal", 0)
macd_div = technical.get("macd_divergence", 0)
stoch_k = technical.get("stoch_k", 0)
stoch_d = technical.get("stoch_d", 0)
```

---

## 🔧 CONFIG CHO CHIẾN LƯỢC

Trong `config/settings.json`, thêm:

```json
{
  "custom_config": {
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "volume_multiplier": 3.0,
    "min_change": 2.0,
    "risk_reward": 2.5,
    "position_size": 2.5
  }
}
```

Trong code:
```python
def __init__(self, config: Dict = None):
    default_config = {
        "rsi_oversold": 30,
        # ... các config khác
    }
    if config:
        default_config.update(config)
```

---

## 📊 SCORING SYSTEM

Tạo confidence score (1-10):

```python
confidence = 0

# Mỗi điều kiện thỏa = +points
if condition1:
    confidence += 3  # Strong signal
if condition2:
    confidence += 2  # Medium signal
if condition3:
    confidence += 1  # Weak signal

# Minimum threshold
if confidence >= 5:
    # Generate signal
```

**Khuyến nghị:**
- Strong condition (quan trọng nhất): +2 to +3
- Medium condition: +1 to +2
- Weak condition (bổ sung): +1
- Negative condition (cảnh báo): -1 to -2

---

## ✅ CHECKLIST TẠO CHIẾN LƯỢC

- [ ] Xác định entry conditions rõ ràng
- [ ] Định nghĩa stop loss logic
- [ ] Tính take profit levels
- [ ] Set confidence scoring
- [ ] Thêm validation rules
- [ ] Test với data thật
- [ ] Backtest (nếu có)
- [ ] Document logic
- [ ] Set reasonable R:R (>= 1:2)
- [ ] Add position sizing

---

## 🚀 SỬ DỤNG CHIẾN LƯỢC

### **Chạy với custom strategy:**

```bash
./run.sh --mode trade --strategy custom --timeframe 15m
```

### **Test nhanh:**

```bash
cd tradingview-mcp
uv run python ../crypto-trading-system/strategies/custom.py
```

---

## 💡 TIPS

### **1. Start Simple**
Bắt đầu với 2-3 điều kiện đơn giản:
- RSI oversold + Volume spike
- EMA cross + ADX strong
- BB squeeze + Breakout

### **2. Add Confluence**
Kết hợp nhiều indicators:
```python
# Single signal - weak
if rsi < 30:
    confidence += 1

# Multiple signals - strong
if rsi < 30 and volume > avg*3 and price > ema50:
    confidence += 5
```

### **3. Risk Management First**
Luôn có:
- Stop loss rõ ràng
- R:R >= 1:2
- Position size <= 3%

### **4. Backtest**
Test chiến lược với data quá khứ trước khi trade thật.

### **5. Iterate**
- Test → Measure → Improve → Repeat
- Theo dõi win rate
- Điều chỉnh parameters

---

## 📚 LEARNING RESOURCES

### **Bollinger Bands:**
- https://tradingview.com/wiki/Bollinger_Bands
- Hiểu về squeeze, breakout, mean reversion

### **RSI:**
- https://tradingview.com/wiki/Relative_Strength_Index
- Overbought/oversold levels
- Divergence patterns

### **Volume Analysis:**
- Volume confirmation
- Volume profile
- Volume-weighted indicators

### **Risk Management:**
- Position sizing formulas
- Kelly Criterion
- Risk of ruin

---

## ❓ FAQ

**Q: Tôi không biết code Python?**
A: Template có sẵn comments chi tiết, chỉ cần điền logic vào. Copy paste các ví dụ và sửa numbers.

**Q: Làm sao biết chiến lược tốt?**
A: Backtest với data quá khứ. Win rate >50% + R:R >1:2 là tốt.

**Q: Có thể combine nhiều chiến lược?**
A: Có! Tạo nhiều strategy files, run từng cái và so sánh signals.

**Q: Indicators nào quan trọng nhất?**
A: Không có "best indicator". Phụ thuộc style của bạn. Trend followers dùng MA, mean reversion dùng RSI/BB.

**Q: Custom strategy không generate signals?**
A: Check confidence threshold. Có thể giảm MIN_CONFIDENCE hoặc adjust điều kiện.

---

## 🎯 NEXT STEPS

1. **Đọc STRATEGY_EXPLAINED.md** - Hiểu breakout strategy
2. **Viết ý tưởng** - Note down entry/exit rules
3. **Code logic** - Điền vào custom.py
4. **Test** - Run và xem signals
5. **Optimize** - Điều chỉnh parameters
6. **Use** - Trade với confidence!

---

**Bạn đã sẵn sàng tạo chiến lược riêng chưa?** 🚀

File template: `strategies/custom.py`
Examples included in this guide above!
