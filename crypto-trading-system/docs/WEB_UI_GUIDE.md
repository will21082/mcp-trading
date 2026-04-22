# 🎨 WEB UI GUIDE - Giao diện React

**Crypto Trading Scanner Web UI**
**Version:** 1.0
**Updated:** 2025-11-03

---

## 🌟 **TỔNG QUAN**

Web UI là giao diện đồ họa đẹp mắt cho hệ thống scan crypto. Thay vì chạy terminal commands, bạn có thể:

✅ Click nút "Scan Now" để trigger scan
✅ Xem dashboard real-time với số liệu
✅ Xem bảng signals LONG/SHORT đầy đủ
✅ Filter theo direction (ALL/LONG/SHORT)
✅ Responsive design - works trên mọi devices

---

## 🚀 **CÁCH SỬ DỤNG**

### **Option 1: Start Script (Đơn giản nhất!)** ⭐

```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
./start.sh
```

Script sẽ tự động:
- ✅ Start backend API (port 5000)
- ✅ Start React frontend (port 3000)
- ✅ Open browser

**Sau đó truy cập:** `http://localhost:3000`

---

### **Option 2: Manual Start (2 Terminals)**

**Terminal 1 - Backend API:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
source venv/bin/activate
python server.py
```

✅ API chạy tại: `http://localhost:5000`

**Terminal 2 - React UI:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
npm run dev
```

✅ UI chạy tại: `http://localhost:3000`

---

## 📊 **GIAO DIỆN CHÍNH**

### **1. Header**
```
🚀 Crypto Trading Scanner
Bybit Breakout Strategy - 15m Timeframe
```

### **2. Scan Button**
```
[🔍 Scan Now]
```
- Click để trigger scan
- Hiển thị spinner khi đang scan
- Scan time: 30-60 giây

### **3. Dashboard (6 cards)**
```
🕐 Last Scan        | 🪙 Coins Scanned
🟢 LONG Signals     | 🔴 SHORT Signals
🎯 Total Signals    | 📊 Success Rate
```

### **4. Results Table**

**Filter buttons:**
```
[All (10)] [🟢 LONG (7)] [🔴 SHORT (3)]
```

**Table columns:**
- **#** - Rank (1, 2, 3...)
- **Symbol** - Coin name (AAVE, AXS, etc.)
- **Direction** - LONG or SHORT badge
- **Entry** - Entry price
- **TP1 (70%)** - First target (close 70%)
- **TP2 (30%)** - Second target (close 30%)
- **Stop Loss** - Stop loss price
- **R:R** - Risk/Reward ratio
- **Quality** - Quality score with stars

**Quality badges:**
- ⭐⭐⭐ 12-15 points - Exceptional
- ⭐⭐ 9-11 points - Excellent
- ⭐ 8 points - Good
- ❌ <8 points - Skip

### **5. Exit Strategy Reminder**
```
⚡ Exit Strategy Reminder:
• Hour 3-4: Close 70% at TP1, move SL to breakeven (0%)
• Hour 4-6: Close remaining 30% at TP2
• Hour 6+: FORCE CLOSE ALL (prevent reversal!)
```

### **6. Strategy Config**
```
📊 Strategy Configuration
Exchange: Bybit | Timeframe: 15m
TP1: +4.5% (Close 70%) | TP2: +7.5% (Close 30%)
Stop Loss: -3% → Breakeven after TP1
Max Hold: 6 hours

🕐 Auto-Scan Schedule:
• 17:00 JST (08:00 UTC) - EU Open
• 21:00 JST (12:00 UTC) - US Open ⭐ BEST!
• 01:00 JST (16:00 UTC) - US Peak
```

---

## 🎯 **WORKFLOW SỬ DỤNG**

### **Bước 1: Khởi động UI**
```bash
cd web-ui
./start.sh
```

### **Bước 2: Mở browser**
```
http://localhost:3000
```

### **Bước 3: Scan market**
```
1. Click nút "Scan Now"
2. Chờ 30-60 giây
3. Xem kết quả xuất hiện
```

### **Bước 4: Đánh giá signals**
```
1. Check dashboard stats
2. Review bảng signals
3. Filter LONG hoặc SHORT
4. Focus vào Quality ≥ 8
5. Note entry, TP1, TP2, SL
```

### **Bước 5: Trade**
```
1. Chọn 2-3 signals tốt nhất
2. Enter tại entry price
3. Set TP1, TP2, SL
4. Set alarms (3-4h, 6h)
5. Apply exit strategy!
```

---

## 🔧 **BACKEND API**

### **Endpoints:**

**1. Health Check**
```
GET /api/health

Response:
{
  "status": "ok",
  "timestamp": "2025-11-03T11:30:00",
  "scanner_exists": true
}
```

**2. Get Configuration**
```
GET /api/config

Response:
{
  "strategy": "Breakout Strategy (15m)",
  "exchange": "Bybit",
  "timeframe": "15m",
  "exit_strategy": { ... },
  "scan_schedule": [ ... ],
  "expected_signals": "6-12 per day",
  "expected_win_rate": "75-80%"
}
```

**3. Get Latest Results**
```
GET /api/results/latest

Response:
{
  "success": true,
  "data": {
    "scan_time": "2025-11-03 11:08 JST",
    "coins_scanned": 84,
    "long_count": 5,
    "short_count": 2,
    "total_signals": 7,
    "signals": [ ... ]
  }
}
```

**4. Trigger New Scan**
```
POST /api/scan

Response:
{
  "success": true,
  "message": "Scan completed successfully",
  "timestamp": "2025-11-03T11:30:00",
  "data": { ... }
}
```

---

## 📱 **RESPONSIVE DESIGN**

### **Desktop (>768px)**
- Full table with all columns
- 6-card dashboard grid
- Large buttons and text

### **Tablet (480-768px)**
- Simplified table
- 2-column dashboard grid
- Medium buttons

### **Mobile (<480px)**
- Essential columns only
- 1-column dashboard
- Stacked layout
- Touch-friendly buttons

---

## 🎨 **DESIGN FEATURES**

### **Color Scheme:**
```
Primary Gradient: #667eea → #764ba2 (Purple)
Success (LONG):   #22c55e (Green)
Danger (SHORT):   #ef4444 (Red)
Background:       Gradient purple backdrop
Cards:            White with shadows
```

### **Animations:**
```
fadeIn  - Smooth entrance
spin    - Loading spinner
pulse   - Attention grabber
hover   - Card lift effect
```

### **Typography:**
```
Font: 'Inter' (Google Fonts)
Headings: 700 weight
Body: 400-500 weight
Monospace: Prices
```

---

## 🐛 **TROUBLESHOOTING**

### **Backend không start:**

**Vấn đề:** `python server.py` fails
**Giải pháp:**
```bash
cd web-ui
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
python server.py
```

---

### **Frontend không start:**

**Vấn đề:** `npm run dev` fails
**Giải pháp:**
```bash
cd web-ui
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

### **CORS errors:**

**Vấn đề:** Browser console shows CORS error
**Giải pháp:**
```bash
# Verify Flask-CORS installed
cd web-ui
source venv/bin/activate
pip install flask-cors

# Check server.py has CORS enabled
grep "CORS" server.py
# Should see: from flask_cors import CORS
#             CORS(app)
```

---

### **Scan không trả về signals:**

**Vấn đề:** 0 signals found

**Nguyên nhân & giải pháp:**

1. **Dead Zone (01:00-08:00 UTC)**
   - ✅ Đợi EU/US session
   - ✅ Scan lúc 17:00, 21:00, 01:00 JST

2. **Backend không chạy**
   - ✅ Check `http://localhost:5000/api/health`
   - ✅ Restart backend server

3. **Scanner lỗi**
   - ✅ Check logs: `../logs/latest_scan.log`
   - ✅ Test manual: `cd .. && uv run python analyzers/bybit_long_short_scanner.py`

---

### **Port already in use:**

**Backend (5000):**
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

**Frontend (3000):**
```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>
```

---

## 🔒 **BẢO MẬT**

### **Local only:**
- ✅ Backend: `host='0.0.0.0'` nhưng firewall blocks external
- ✅ Frontend: `localhost:3000` only
- ✅ No authentication required (local use)

### **API Keys:**
- ✅ Stored in parent project (`../config/`)
- ✅ NOT in web-ui directory
- ✅ Backend reads from parent

### **Best Practices:**
- ❌ Don't expose to internet
- ❌ Don't commit API keys
- ✅ Use for local development only

---

## 📈 **PERFORMANCE**

### **Metrics:**
```
Initial Load:     < 1 second
Scan Trigger:     30-60 seconds (84 coins)
API Response:     < 1 second (cached)
Table Render:     < 100ms (up to 50 signals)
```

### **Optimization:**
- React memo for components
- CSS animations (GPU accelerated)
- Debounced filter updates
- Lazy loading for images

---

## 🎓 **DEVELOPMENT GUIDE**

### **Adding New Feature:**

**1. Backend (server.py):**
```python
@app.route('/api/newfeature', methods=['POST'])
def new_feature():
    # Your logic
    return jsonify({'success': True, 'data': result})
```

**2. Frontend (App.jsx):**
```javascript
const handleNewFeature = async () => {
  const response = await axios.post(`${API_BASE}/newfeature`)
  // Handle response
}
```

**3. Component (NewComponent.jsx):**
```javascript
function NewComponent({ data, onAction }) {
  return <div>Your UI</div>
}
```

**4. Styling (NewComponent.css):**
```css
.new-component {
  /* Your styles */
}
```

---

### **File Structure:**
```
web-ui/
├── src/
│   ├── components/          ← React components
│   │   ├── Dashboard.jsx
│   │   ├── ScanButton.jsx
│   │   └── ResultsTable.jsx
│   ├── App.jsx             ← Main app
│   ├── main.jsx            ← Entry point
│   └── index.css           ← Global styles
├── server.py               ← Flask backend
├── vite.config.js          ← Vite config
├── package.json            ← Dependencies
├── start.sh               ← Startup script
├── README.md              ← Full documentation
└── QUICKSTART.md          ← Quick guide
```

---

## 📚 **TÀI LIỆU LIÊN QUAN**

**Web UI:**
- `web-ui/README.md` - Full documentation
- `web-ui/QUICKSTART.md` - Quick start guide

**Trading System:**
- `docs/STRATEGY_OPTIMIZATION_ANALYSIS.md` - Exit strategy
- `docs/CRON_SCHEDULE_US_EU.md` - Scan schedule
- `docs/QUICK_REFERENCE.md` - Quick reference

---

## 💡 **PRO TIPS**

### **1. Keep Both Terminals Visible**
- Terminal 1: Backend logs
- Terminal 2: Frontend logs
- Dễ debug khi có lỗi!

### **2. Use Browser DevTools**
- F12 để mở console
- Network tab: Check API calls
- Console tab: Check errors

### **3. Auto-reload**
- Vite auto-reloads khi sửa code
- Flask debug mode auto-reloads backend
- No need to restart!

### **4. Test API Directly**
```bash
# Health check
curl http://localhost:5000/api/health

# Get latest results
curl http://localhost:5000/api/results/latest

# Trigger scan
curl -X POST http://localhost:5000/api/scan
```

### **5. Production Build**
```bash
npm run build
npm run preview
# Serve from dist/
```

---

## 🎯 **TÍCH HỢP VỚI HỆ THỐNG**

### **Web UI ↔ Scanner:**
```
React UI → Flask API → bybit_long_short_scanner.py → Results
```

### **Web UI ↔ Reports:**
```
UI requests → API parses → reports/scans/BYBIT_LONG_SHORT_OPTIMIZED.md
```

### **Web UI ↔ Cron Jobs:**
```
Cron runs → Scanner updates report → UI fetches latest results
```

**Advantage:** Web UI có thể xem cả:
- Manual scans (từ nút Scan Now)
- Automatic scans (từ cron jobs)

---

## 🚀 **NEXT STEPS**

**Đã hoàn thành:**
- ✅ React UI đẹp
- ✅ Flask backend API
- ✅ Dashboard real-time
- ✅ Signal table với filter
- ✅ Responsive design
- ✅ Start script

**Có thể thêm (future):**
- 📧 Email notifications toggle trong UI
- 📊 Charts (TradingView integration)
- 🔔 Browser notifications
- 📱 PWA (install as app)
- 🌙 Dark mode toggle
- 📈 Historical scan results
- 🔄 Auto-refresh every N minutes

---

## 🎉 **SUMMARY**

**Web UI cho phép:**
1. ✅ Scan market với 1 click
2. ✅ Xem dashboard real-time
3. ✅ Xem tất cả signals LONG/SHORT
4. ✅ Filter & sort signals
5. ✅ Check quality scores
6. ✅ Note entry/exit prices
7. ✅ Hiểu exit strategy
8. ✅ Works trên mọi devices

**Quick Start:**
```bash
cd web-ui
./start.sh
# Open: http://localhost:3000
```

**Expected Experience:**
- 🎨 Beautiful gradient UI
- ⚡ Fast & responsive
- 📊 Clear data presentation
- 🎯 Easy to use
- 💰 Focus on trading!

---

**Enjoy the UI! Happy Trading! 🚀💰**
