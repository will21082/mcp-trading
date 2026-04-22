# 📊 REPORTS FOLDER

Folder tổng hợp tất cả báo cáo trading và phân tích.

---

## 📁 CẤU TRÚC

```
reports/
│
├── 📋 INDEX.md              ← Tổng hợp tất cả báo cáo (XEM ĐÂY TRƯỚC!)
├── 📖 README.md             ← File này
│
├── 🔍 scans/                ← Market scan results
│   └── BYBIT_SCAN_RESULTS.md
│
├── 🎯 signals/              ← Trade signals generated
│   └── (auto-generated)
│
├── 💼 trades/               ← Trade history & logs
│   └── (manual or auto)
│
├── 📊 performance/          ← Performance reports
│   └── (weekly/monthly)
│
└── 📦 archive/              ← Old reports
    └── (>30 days)
```

---

## 🚀 QUICK START

### **1. Xem báo cáo mới nhất:**
```bash
cat INDEX.md
```

### **2. Xem Bybit scan results:**
```bash
cat scans/BYBIT_SCAN_RESULTS.md
```

### **3. Tạo báo cáo mới:**
```bash
cd ..
./run.sh --mode scan --timeframe 15m
```

---

## 📊 BÁO CÁO HIỆN CÓ

### **Scans:**
- ✅ BYBIT_SCAN_RESULTS.md - Bybit 15m breakout scan

### **Signals:**
- (Xem trong ../data/signals_*.json)

### **Trades:**
- (Chưa có - sẽ được tạo khi execute)

### **Performance:**
- (Xem trong ../data/risk_state.json)

---

## 🎯 CÁCH TẠO BÁO CÁO MỚI

### **Automatic (Recommended):**

System tự động lưu:
- Market scans → `../data/signals_*.json`
- Trade signals → `../data/trade_signals_*.json`
- Portfolio state → `../data/risk_state.json`

### **Manual Report:**

Copy template và điền thông tin:

```bash
# Copy template
cp templates/scan_template.md scans/KUCOIN_SCAN_$(date +%Y%m%d).md

# Edit
nano scans/KUCOIN_SCAN_*.md
```

---

## 📋 TEMPLATES

### **Scan Report Template:**

```markdown
# [EXCHANGE] Scan - [STRATEGY]

Date: YYYY-MM-DD HH:MM
Timeframe: 15m/1h/4h
Exchange: KUCOIN/BYBIT
Strategy: Breakout/Custom

## Summary
Total scanned: XX
Signals found: XX
Top confidence: XX/10

## Top Opportunities
1. SYMBOL - XX/10
   - Price: $X.XX
   - Reasons: ...

## Recommendations
...
```

---

## 🔄 MAINTENANCE

### **Archive old reports:**
```bash
# Move reports >30 days to archive
find scans/ -name "*.md" -mtime +30 -exec mv {} archive/ \;
```

### **Clean up:**
```bash
# Remove very old archives (>90 days)
find archive/ -name "*.md" -mtime +90 -delete
```

---

## 📊 REPORT TYPES

### **1. Market Scans**
- Exchange scans
- Multi-timeframe analysis
- Pattern detection
- Volume analysis

### **2. Trade Signals**
- Entry/exit plans
- Risk/reward calculations
- Confidence scoring
- Validation results

### **3. Trade Logs**
- Entry details
- Exit details
- PNL calculation
- Lessons learned

### **4. Performance**
- Daily/weekly/monthly summaries
- Win rate analysis
- Strategy comparison
- Goal tracking

---

## 🎓 BEST PRACTICES

### **Naming Convention:**

```
scans/[EXCHANGE]_SCAN_[DATE]_[TIMEFRAME].md
signals/[STRATEGY]_SIGNALS_[DATE].md
trades/TRADE_[SYMBOL]_[DATE].md
performance/PERF_[PERIOD]_[DATE].md
```

### **What to Include:**

**Scan Reports:**
- Date & time
- Exchange & timeframe
- Strategy used
- Top opportunities
- Statistics
- Recommendations

**Trade Reports:**
- Entry/exit details
- Risk management
- PNL results
- What worked/didn't work
- Lessons learned

---

## 🔗 LINKS

- [INDEX](INDEX.md) - Tổng hợp báo cáo
- [Main README](../README.md) - Hướng dẫn hệ thống
- [Strategy Explained](../STRATEGY_EXPLAINED.md) - Giải thích chiến lược
- [How to Use](../HOW_TO_USE.md) - Cách sử dụng

---

## 💡 TIPS

1. **Review thường xuyên**: Xem lại báo cáo cũ để học
2. **Track patterns**: Note lại patterns nào work best
3. **Compare strategies**: So sánh performance các strategies
4. **Archive regularly**: Giữ folder gọn gàng
5. **Use INDEX.md**: Luôn update INDEX khi có báo cáo mới

---

**Start Here:** [INDEX.md](INDEX.md)

**Latest Report:** [scans/BYBIT_SCAN_RESULTS.md](scans/BYBIT_SCAN_RESULTS.md)
