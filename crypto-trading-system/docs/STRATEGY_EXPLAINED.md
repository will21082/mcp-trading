# 📘 Giải thích Chiến lược Trading

## 🎯 Chiến lược hiện tại: BREAKOUT STRATEGY

### **Tóm tắt:**
Đây là chiến lược tìm kiếm **Bollinger Band Squeeze** (khi giá nén lại trong dải hẹp) và **Breakout** (khi giá bứt phá ra khỏi dải).

### **Logic chi tiết:**

#### **ĐIỀU KIỆN VÀO LỆNH (BUY):**

```
┌─────────────────────────────────────────────────────────┐
│  BƯỚC 1: Tìm BB Squeeze                                 │
├─────────────────────────────────────────────────────────┤
│  • BBW (Bollinger Band Width) < 0.03                   │
│  • Nghĩa là: Dải BB đang thu hẹp                       │
│  • Tại sao: Sau khi nén, thường có breakout mạnh       │
│  → Điểm: +2 confidence                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BƯỚC 2: Xác nhận Breakout                              │
├─────────────────────────────────────────────────────────┤
│  Bullish Breakout:                                      │
│  • Price > Upper BB                                     │
│  • Change > 2%                                          │
│  → Điểm: +3 confidence                                  │
│                                                         │
│  HOẶC Oversold Bounce:                                  │
│  • Price < Lower BB                                     │
│  • RSI < 30                                             │
│  • Change < -3%                                         │
│  → Điểm: +2 confidence                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BƯỚC 3: RSI Confirmation                               │
├─────────────────────────────────────────────────────────┤
│  • RSI trong khoảng 30-70                              │
│  • Tại sao: Không quá mua/bán                          │
│  → Điểm: +1 confidence                                  │
│                                                         │
│  Nếu RSI > 70:                                          │
│  → Cảnh báo overbought, -1 điểm                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BƯỚC 4: Volume Confirmation                            │
├─────────────────────────────────────────────────────────┤
│  • Volume > 100,000                                     │
│  • Tại sao: Volume cao = sức mạnh thật                 │
│  → Điểm: +1 confidence                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BƯỚC 5: Trend Strength (ADX)                           │
├─────────────────────────────────────────────────────────┤
│  • ADX > 25                                             │
│  • Tại sao: Trend đủ mạnh để theo                      │
│  → Điểm: +1 confidence                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BƯỚC 6: BB Rating                                      │
├─────────────────────────────────────────────────────────┤
│  • BB Rating >= +2 (Strong Buy)                        │
│  → Điểm: +2 confidence                                  │
│                                                         │
│  • BB Rating >= +1 (Weak Buy)                          │
│  → Điểm: +1 confidence                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  QUYẾT ĐỊNH CUỐI CÙNG                                   │
├─────────────────────────────────────────────────────────┤
│  • Tổng điểm >= 5: TẠO SIGNAL                          │
│  • Tổng điểm < 5: SKIP                                 │
└─────────────────────────────────────────────────────────┘
```

#### **VÍ DỤ THỰC TẾ:**

```
Coin: KUCOIN:NAYMUSDT
Price: $0.001300

✓ BBW = 0.0234 < 0.03         → +2 điểm (Squeeze detected)
✓ Price vượt Upper BB +2.5%   → +3 điểm (Bullish breakout)
✓ RSI = 53.4 (trong 30-70)    → +1 điểm (Healthy)
✓ Volume = 178,718 > 100k     → +1 điểm (Good volume)
✓ ADX = 28.5 > 25             → +1 điểm (Strong trend)
✓ BB Rating = +2              → +2 điểm (Strong buy signal)

TỔNG: 10/10 điểm → BUY SIGNAL MẠNH! 🚀
```

---

## 🎓 **STOP LOSS & TAKE PROFIT**

### **Stop Loss Calculation:**

```python
# Method 1: Percentage (Default)
Stop Loss = Entry Price × 0.97  # 3% dưới entry

# Method 2: Bollinger Band
Stop Loss = Lower BB × 0.99     # 1% dưới lower BB
```

**Ví dụ:**
- Entry: $0.001300
- Stop Loss: $0.001261 (3% risk)

### **Take Profit Calculation:**

```python
Risk = Entry - Stop Loss
Reward = Risk × Risk_Reward_Ratio

# Multiple levels:
TP1 = Entry + (Reward × 0.5)   # 50% position
TP2 = Entry + (Reward × 1.0)   # 30% position
TP3 = Entry + (Reward × 1.5)   # 20% position
```

**Ví dụ với R:R = 1:3:**
- Entry: $0.001300
- Stop Loss: $0.001261 (risk = $0.000039)
- Reward target: $0.000117 (3x risk)

Take Profit:
- TP1: $0.001358 (+4.46%) - Chốt 50% lãi
- TP2: $0.001417 (+9.00%) - Chốt 30% lãi
- TP3: $0.001475 (+13.46%) - Để chạy 20%

---

## 🔧 **TÙY CHỈNH CHIẾN LƯỢC**

### **File config:** `config/settings.json`

```json
{
  "breakout_config": {
    "bbw_threshold": 0.03,        // ← Điều chỉnh ở đây
    "volume_multiplier": 2.0,
    "rsi_min": 30,
    "rsi_max": 70,
    "risk_reward": 3.0,           // ← Target R:R
    "position_size": 2.0          // ← % vốn mỗi lệnh
  }
}
```

### **Ý nghĩa từng tham số:**

| Tham số | Mặc định | Ý nghĩa | Điều chỉnh |
|---------|----------|---------|------------|
| `bbw_threshold` | 0.03 | Ngưỡng BB squeeze | Giảm = chặt hơn (ít signal) |
| `volume_multiplier` | 2.0 | Volume phải >2x avg | Tăng = yêu cầu volume cao hơn |
| `rsi_min` | 30 | RSI tối thiểu | Tăng = ít oversold signals |
| `rsi_max` | 70 | RSI tối đa | Giảm = tránh overbought |
| `risk_reward` | 3.0 | Target R:R | Tăng = target xa hơn |
| `position_size` | 2.0% | % vốn mỗi lệnh | Max 5% khuyến nghị |

---

## ✍️ **TẠO CHIẾN LƯỢC RIÊNG CỦA BẠN**

### **Template:** `strategies/custom.py`

Tôi sẽ tạo file template để bạn dễ dàng tạo chiến lược riêng!

**Các bước:**
1. Copy template `custom.py`
2. Điền logic của bạn
3. Test chiến lược
4. Sử dụng: `./run.sh --mode trade --strategy custom`

---

## 🤔 **Ý TƯỞNG CHIẾN LƯỢC KHÁC**

### **1. RSI Divergence Strategy**
- Tìm RSI divergence (giá tăng, RSI giảm)
- Entry khi divergence + volume spike
- Target: Short-term reversal

### **2. EMA Crossover Strategy**
- EMA50 cắt lên EMA200 (Golden Cross)
- Volume confirmation
- Target: Trend following

### **3. Support/Resistance Breakout**
- Tìm level S/R quan trọng
- Breakout + retest
- Target: Medium-term trend

### **4. Volume Profile Strategy**
- Tìm volume clustering
- Entry ở low volume node
- Target ở high volume node

### **5. Multi-Timeframe Strategy**
- 1D: Xác định trend
- 4H: Tìm entry zone
- 15m: Timing chính xác

---

## 📊 **KHI NÀO DÙNG BREAKOUT STRATEGY?**

### ✅ **PHÙ HỢP:**
- Thị trường sideway → chuẩn bị breakout
- Volatility thấp → có thể bùng nổ
- Coins có volume ổn định
- Timeframe: 15m - 4h

### ❌ **KHÔNG PHÙ HỢP:**
- Thị trường trending mạnh
- Volatility cực cao
- Low volume coins
- Breaking news events

---

## 💡 **TIPS SỬ DỤNG:**

### **1. Confirm trên nhiều timeframes**
```bash
# Scan 1h tìm coins
./run.sh --mode scan --timeframe 1h

# Confirm trên 15m
./run.sh --mode scan --timeframe 15m

# Generate signal
./run.sh --mode trade --strategy breakout --timeframe 15m
```

### **2. Check BB Width trend**
- BBW đang thu hẹp → Tốt (squeeze tăng)
- BBW đang mở rộng → Cẩn thận (có thể muộn)

### **3. Volume là key**
- Volume tăng khi breakout → Thật
- Volume thấp khi breakout → Fake

### **4. Confluence signals**
Càng nhiều lý do → Signal càng mạnh:
- BB Squeeze ✓
- Volume spike ✓
- RSI healthy ✓
- Trend strong ✓
- Support/Resistance level ✓

---

## 🎯 **NEXT STEPS**

Bạn muốn:
1. **Hiểu sâu hơn về Breakout Strategy?** → Tôi giải thích chi tiết từng phần
2. **Tạo chiến lược riêng?** → Tôi tạo template và hướng dẫn
3. **Optimize config?** → Tôi giúp điều chỉnh parameters
4. **Backtest?** → Tôi tạo module backtest

**Bạn muốn làm gì tiếp theo?** 🚀
