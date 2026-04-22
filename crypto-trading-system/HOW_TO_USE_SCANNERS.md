# 🚀 HƯỚNG DẪN SỬ DỤNG BYBIT BREAKOUT SCANNERS

## 📦 CÁC TOOL ĐÃ TẠO

Bạn có 3 scanners để tìm signal breakout trên Bybit:

### 1. 🎯 Bybit Breakout Scanner (Chất lượng cao)
**File:** `bybit_breakout_scanner.py`

**Đặc điểm:**
- Threshold CAO (Quality ≥ 8/20, Breakout Strength ≥ 3)
- Tập trung vào setup HOÀN HẢO
- Phù hợp: Swing trading 2-7 ngày
- Ít signal nhưng chất lượng cao

**Khi nào dùng:**
- Khung 4H hoặc 1D
- Muốn hold lâu hơn
- Tìm setup an toàn nhất

**Cách dùng:**
```bash
# Activate venv
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system"
source "../tradingview-mcp/.venv/bin/activate"

# Scan trên khung 4H
python3 bybit_breakout_scanner.py --timeframe 4h --top 15

# Scan trên khung 1H
python3 bybit_breakout_scanner.py --timeframe 1h --top 20

# Scan chỉ midcap
python3 bybit_breakout_scanner.py --timeframe 4h --midcap-only --top 10
```

---

### 2. ⚡ Quick Scanner (Nhanh, nhiều signal)
**File:** `bybit_quick_scanner.py`

**Đặc điểm:**
- Threshold THẤP HƠN (Confidence ≥ 5/10)
- Nhiều signal hơn
- Phù hợp: Intraday, scalping
- Nhanh chóng, flexible

**Khi nào dùng:**
- Khung 15M hoặc 1H
- Muốn trade nhiều hơn
- Scalping, day trading

**Cách dùng:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system"
source "../tradingview-mcp/.venv/bin/activate"

# Scan 15M cho scalping
python3 bybit_quick_scanner.py --timeframe 15m --top 20

# Scan 1H cho intraday
python3 bybit_quick_scanner.py --timeframe 1h --top 15
```

---

### 3. 📊 Market Status Checker
**File:** `check_market_status.py`

**Đặc điểm:**
- KHÔNG tìm signal
- Hiển thị tổng quan thị trường
- Phân tích BB Rating, BBW, RSI, ADX
- Khuyến nghị có nên trade không

**Khi nào dùng:**
- Trước khi scan signal
- Kiểm tra market sentiment
- Quyết định có nên trade hôm nay

**Cách dùng:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system"
source "../tradingview-mcp/.venv/bin/activate"

# Check market trên 15M
python3 check_market_status.py --timeframe 15m

# Check market trên 1H
python3 check_market_status.py --timeframe 1h

# Check market trên 4H
python3 check_market_status.py --timeframe 4h
```

---

## 🎯 WORKFLOW KHUYẾN NGHỊ

### 📅 Daily Routine:

#### Bước 1: Check Market Status (Sáng 8:00)
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system"
source "../tradingview-mcp/.venv/bin/activate"
python3 check_market_status.py --timeframe 4h
```

**Đọc kết quả:**
- Nếu có "Potential Opportunities" → Tiếp tục Bước 2
- Nếu "WAIT FOR BETTER SETUP" → Đợi, check lại sau 4-8 giờ

#### Bước 2: Scan Signal (Nếu market OK)
```bash
# Swing trading (hold 2-7 ngày)
python3 bybit_breakout_scanner.py --timeframe 4h --top 15

# Hoặc intraday (hold vài giờ)
python3 bybit_quick_scanner.py --timeframe 1h --top 20
```

#### Bước 3: Phân tích Signal
Khi tìm thấy signal, kiểm tra:

**A. Chất lượng Signal:**
- ✅ Quality Score ≥ 8/20 (tốt nhất ≥ 12)
- ✅ Breakout Strength ≥ 3/10
- ✅ Confidence ≥ 7/10
- ✅ Coin type = MIDCAP (ưu tiên)

**B. Technicals:**
- ✅ BB Width < 0.030 (squeeze)
- ✅ BB Rating ≥ +2
- ✅ RSI 45-60 (healthy momentum)
- ✅ ADX > 25 (có trend)
- ✅ EMA Trend = "Golden Cross"

**C. Risk Management:**
- ✅ R:R Ratio ≥ 1:2.5
- ✅ Stop Loss không quá xa (< 5%)
- ✅ Entry price hợp lý

#### Bước 4: Verify trên TradingView
1. Mở chart coin trên TradingView
2. Kiểm tra:
   - BB bands có squeeze không?
   - Price đang ở đâu so với BB?
   - Volume có tăng không?
   - Order book có support không?
3. Confirm signal

#### Bước 5: Entry
Nếu tất cả OK:
1. **Entry:** Giá hiện tại hoặc đợi pullback
2. **Stop Loss:** Theo signal (thường -3% đến -4%)
3. **Take Profit:**
   - TP1: Close 40% position
   - TP2: Close 40% position
   - TP3: Trail 20% còn lại
4. **Position Size:** 2-3% capital

---

## ⏰ LỊCH SCAN TRONG NGÀY

### Nếu trade khung 4H (Swing):
- **08:00:** Check market status + Scan 4H
- **16:00:** Scan lại 4H
- **00:00:** Final scan 4H

### Nếu trade khung 1H (Intraday):
- **08:00:** Check market + Scan 1H
- **12:00:** Scan 1H
- **16:00:** Scan 1H
- **20:00:** Scan 1H

### Nếu scalping khung 15M:
- Scan mỗi 2-3 giờ
- Hoặc setup cron job tự động

---

## 🔧 SETUP AUTO SCAN (Optional)

### Tạo script tự động:
```bash
# File: auto_scan.sh
#!/bin/bash

cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system"
source "../tradingview-mcp/.venv/bin/activate"

echo "=== Market Status ==="
python3 check_market_status.py --timeframe 4h

echo ""
echo "=== Breakout Scan ==="
python3 bybit_breakout_scanner.py --timeframe 4h --top 10
```

### Chạy định kỳ với cron:
```bash
# Edit crontab
crontab -e

# Add này vào:
# Scan mỗi 4 giờ
0 */4 * * * cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system" && bash auto_scan.sh
```

---

## 📊 ĐỌC KẾT QUẢ SCAN

### Format Output:

```
======================================================================
#1 - APTUSDT [MIDCAP] - 4h
======================================================================
Confidence: 9/10 🔥🔥🔥🔥🔥🔥🔥🔥🔥
Breakout Strength: 8/10 💥💥💥💥💥💥💥💥
Quality: 15/25 ⭐⭐⭐

💰 ENTRY: $12.345678

🎯 TARGETS:
  TP1: $12.8 (+3.68%) - Close 40%
  TP2: $13.5 (+9.35%) - Close 40%
  TP3: $14.2 (+15.02%) - Trail 20%

🛡️ STOP: $11.9 (-3.61%)
R:R: 1:2.6

📊 BREAKOUT ANALYSIS:
  BB Width: 0.0185 (TIGHT!)
  BB Position: Above Upper (BREAKOUT!)
  BB Rating: +3

📈 TECHNICALS:
  RSI: 54.2 (Perfect zone)
  ADX: 32.5 (Strong trend)
  EMA Trend: Golden Cross
  MACD: Bullish

✅ REASONS:
  • 🔥🔥🔥 BB Rating: +3 - EXTREME strength
  • 💥💥 BB VERY TIGHT: 0.0185 - Big breakout building
  • 🚀🚀 BREAKOUT ABOVE BB UPPER - Strong bullish!
  • ✅✅ RSI Perfect Zone: 54.2 - Ideal entry!
  • 💪 ADX Strong: 32.5
  • 💎 Golden Cross - Price > EMA50 > EMA200
```

### Giải thích:

**Confidence 9/10:** Rất tin tưởng vào signal này
**Breakout Strength 8/10:** Breakout rất mạnh
**Quality 15/25:** Setup tốt (>12 là excellent)

**Targets:**
- TP1: Exit nhanh 40% để lock profit
- TP2: Main target, exit 40%
- TP3: Let it run 20%, dùng trailing stop

**Key Points:**
- BB Width càng nhỏ (<0.020) = càng tốt
- BB Position "Above Upper" = confirmed breakout
- RSI 45-60 = healthy
- ADX >25 = có trend
- Golden Cross = best structure

---

## ⚠️ LƯU Ý QUAN TRỌNG

### ✅ DO:
1. **Luôn kiểm tra market status TRƯỚC KHI SCAN**
2. **Verify signal trên TradingView**
3. **Tôn trọng Stop Loss - KHÔNG move SL**
4. **Take profit từng phần theo kế hoạch**
5. **Log trades để review**
6. **Chỉ trade khi signal đạt threshold**

### ❌ DON'T:
1. **Không force trade khi không có signal**
2. **Không ignore warnings trong output**
3. **Không trade quá nhiều signals cùng lúc**
4. **Không over-leverage**
5. **Không FOMO vào coin đã pump mạnh**
6. **Không bỏ qua risk management**

---

## 🎓 HIỂU VỀ BREAKOUT STRATEGY

### Breakout là gì?
Price phá vỡ một vùng consolidation (BB squeeze) với volume cao, bắt đầu một xu hướng mới.

### Điều kiện hoàn hảo:
1. **Consolidation:** BBW < 0.030 (càng nhỏ càng tốt)
2. **Direction:** BB Rating ≥ +2, price > BB Upper
3. **Momentum:** RSI 45-60, ADX >25
4. **Structure:** Golden Cross (Price > EMA50 > EMA200)
5. **Volume:** Tăng mạnh khi breakout

### Tại sao ưu tiên Midcap?
- **Higher volatility** = Bigger moves
- **Lower market cap** = Dễ pump hơn
- **Less manipulation** than small cap
- **More upside** than large cap
- **Good liquidity** on Bybit

### Best Midcap Sectors:
- **DeFi:** AAVE, MKR, CRV, COMP
- **Layer 1/2:** APT, NEAR, SUI, OP, ARB, INJ
- **AI:** RENDER, FET, GRT
- **Gaming:** SAND, AXS, IMX

---

## 📞 TROUBLESHOOTING

### Vấn đề: Không tìm thấy signal
**Giải pháp:**
1. Check market status trước
2. Thị trường có thể đang sideways → đợi
3. Thử timeframe khác (4H → 1H → 15M)
4. Đợi 2-4 giờ scan lại

### Vấn đề: Quá nhiều signal
**Giải pháp:**
1. Tăng threshold trong code
2. Chỉ lấy top 3-5 signals
3. Chọn MIDCAP với Quality cao nhất

### Vấn đề: Script báo lỗi
**Giải pháp:**
```bash
# Reinstall dependencies
cd "/Users/will208/Desktop/MCP Trading /tradingview-mcp"
source .venv/bin/activate
pip install -r requirements.txt
```

### Vấn đề: Data không load
**Giải pháp:**
1. Check internet connection
2. TradingView có thể rate limit → đợi 5-10 phút
3. Thử lại với ít coins hơn

---

## 📈 TRACKING PERFORMANCE

### Tạo Trading Journal:
```bash
# File: trades.csv
Date,Symbol,Type,Entry,SL,TP1,TP2,Result,Profit%,Notes
2025-11-03,APTUSDT,MIDCAP,12.34,11.90,12.80,13.50,WIN,+7.5%,Perfect breakout
```

### Review hàng tuần:
- Win rate
- Average R:R
- Best performing sectors
- Common mistakes
- Adjust strategy

---

## 🎯 FINAL TIPS

1. **Patience:** Breakout strategy cần đợi setup đúng
2. **Discipline:** Không trade nếu không có signal
3. **Risk Management:** Luôn dùng SL, size position đúng
4. **Focus on Midcap:** Higher potential
5. **Multiple Timeframes:** Verify signal trên nhiều TF
6. **Journal Everything:** Learn from winners AND losers

---

**Good luck với trading! 🚀**

Remember: **The best trade is the one you DON'T take when setup isn't perfect!**
