# 🎨 WEB UI - SCRIPTS HƯỚNG DẪN

**Quick reference cho các scripts quản lý Web UI**

---

## 📂 **CÁC SCRIPTS**

Bạn có 3 scripts chính để quản lý Web UI:

```
crypto-trading-system/
├── run_webui.sh      ← Start both backend + frontend
├── stop_webui.sh     ← Stop all services
└── status_webui.sh   ← Check status
```

---

## 🚀 **1. START WEB UI**

### **run_webui.sh**

**Mục đích:** Start cả Backend (Flask) và Frontend (React) trong một lệnh

**Cách dùng:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system"
./run_webui.sh
```

**Script sẽ:**
1. ✅ Check Python, Node.js, npm
2. ✅ Setup virtual environment (nếu chưa có)
3. ✅ Install dependencies (nếu chưa có)
4. ✅ Check & free ports 5000, 3000
5. ✅ Start Flask backend (port 5000)
6. ✅ Start React frontend (port 3000)
7. ✅ Display URLs và instructions
8. ✅ Keep running until Ctrl+C

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║        🚀 CRYPTO TRADING SCANNER - WEB UI LAUNCHER        ║
║             Bybit Breakout Strategy - 15m Timeframe            ║
╚════════════════════════════════════════════════════════════════╝

🔍 Checking prerequisites...
✅ Python: Python 3.x.x
✅ Node.js: v18.x.x
✅ npm: v9.x.x

✅ Virtual environment found
✅ Node modules found

🔌 Checking ports...
✅ Port 5000 available
✅ Port 3000 available

════════════════════════════════════════════════════════════════
🔧 Starting Backend API Server...
════════════════════════════════════════════════════════════════

✅ Backend started successfully!
   PID: 12345
   URL: http://localhost:5000
   Log: /tmp/crypto_scanner_backend.log

════════════════════════════════════════════════════════════════
⚛️  Starting React Frontend...
════════════════════════════════════════════════════════════════

✅ Frontend started successfully!
   PID: 12346
   URL: http://localhost:3000
   Log: /tmp/crypto_scanner_frontend.log

════════════════════════════════════════════════════════════════
✨ WEB UI IS READY! ✨
════════════════════════════════════════════════════════════════

🌐 Access the application:

   Frontend UI:  http://localhost:3000  ⭐ Open this!
   Backend API:  http://localhost:5000

════════════════════════════════════════════════════════════════

📊 How to use:
   1. Open http://localhost:3000 in your browser
   2. Click "🔍 Scan Now" button
   3. Wait 30-60 seconds for scan to complete
   4. Review signals in dashboard and table
   5. Trade on signals with Quality ≥ 8

⚡ Exit Strategy:
   • Hour 3-4: Close 70% at TP1, move SL to breakeven
   • Hour 4-6: Close remaining 30% at TP2
   • Hour 6+:  FORCE CLOSE ALL (prevent reversal!)

════════════════════════════════════════════════════════════════

⚠️  Press Ctrl+C to stop both services
```

**Dừng services:**
- Press `Ctrl+C` hoặc
- Run `./stop_webui.sh`

**Logs:**
```bash
# Backend log
tail -f /tmp/crypto_scanner_backend.log

# Frontend log
tail -f /tmp/crypto_scanner_frontend.log
```

---

## 🛑 **2. STOP WEB UI**

### **stop_webui.sh**

**Mục đích:** Dừng tất cả services (Backend + Frontend)

**Cách dùng:**
```bash
./stop_webui.sh
```

**Script sẽ:**
1. ✅ Stop backend using PID file
2. ✅ Stop frontend using PID file
3. ✅ Force kill processes on port 5000, 3000 (nếu còn)
4. ✅ Kill remaining Python server.py processes
5. ✅ Kill remaining Vite processes
6. ✅ Clean up PID files

**Output:**
```
════════════════════════════════════════════════════════════════
🛑 Stopping Crypto Scanner Web UI...
════════════════════════════════════════════════════════════════

✅ Backend stopped (PID: 12345)
✅ Frontend stopped (PID: 12346)

✨ All services stopped successfully!

════════════════════════════════════════════════════════════════
```

**Khi nào dùng:**
- Khi muốn stop services mà không dùng Ctrl+C
- Khi services bị "zombie" (chạy background)
- Khi cần free ports 5000, 3000

---

## 📊 **3. CHECK STATUS**

### **status_webui.sh**

**Mục đích:** Check status của Backend và Frontend

**Cách dùng:**
```bash
./status_webui.sh
```

**Script sẽ:**
1. ✅ Check port 5000 (Backend)
2. ✅ Check port 3000 (Frontend)
3. ✅ Test API health endpoint
4. ✅ Test Frontend accessibility
5. ✅ Show process details
6. ✅ Show log file info
7. ✅ Show quick actions

**Output khi RUNNING:**
```
════════════════════════════════════════════════════════════════
📊 Crypto Scanner Web UI - Status Check
════════════════════════════════════════════════════════════════

🔧 Backend API (Flask):

   Status:  ✅ RUNNING
   PID:     12345
   Port:    5000
   URL:     http://localhost:5000
   Health:  ✅ API responding

⚛️  Frontend (React):

   Status:  ✅ RUNNING
   PID:     12346
   Port:    3000
   URL:     http://localhost:3000
   Health:  ✅ UI accessible

════════════════════════════════════════════════════════════════

✨ Overall Status: FULLY OPERATIONAL

   🌐 Access the UI: http://localhost:3000

📋 Process Details:

   Python (server.py):
      PID: 12345 python server.py

   Vite (React):
      PID: 12346 vite

📄 Log Files:

   Backend:  /tmp/crypto_scanner_backend.log (5.2K)
   Frontend: /tmp/crypto_scanner_frontend.log (12K)

⚡ Quick Actions:

   Start:    ./run_webui.sh
   Stop:     ./stop_webui.sh
   Status:   ./status_webui.sh

   Logs:     tail -f /tmp/crypto_scanner_backend.log
             tail -f /tmp/crypto_scanner_frontend.log

════════════════════════════════════════════════════════════════
```

**Output khi NOT RUNNING:**
```
════════════════════════════════════════════════════════════════
📊 Crypto Scanner Web UI - Status Check
════════════════════════════════════════════════════════════════

🔧 Backend API (Flask):

   Status:  ❌ NOT RUNNING
   Port:    5000 (not listening)

⚛️  Frontend (React):

   Status:  ❌ NOT RUNNING
   Port:    3000 (not listening)

════════════════════════════════════════════════════════════════

❌ Overall Status: NOT RUNNING

   To start: ./run_webui.sh

📋 Process Details:

   No Web UI processes running

📄 Log Files:

   Backend:  No log file
   Frontend: No log file

⚡ Quick Actions:

   Start:    ./run_webui.sh
   Stop:     ./stop_webui.sh
   Status:   ./status_webui.sh

════════════════════════════════════════════════════════════════
```

**Khi nào dùng:**
- Check xem services có đang chạy không
- Xem PID của processes
- Xem log file size
- Troubleshooting

---

## 🔧 **TROUBLESHOOTING**

### **Problem 1: Port already in use**

**Symptom:**
```
⚠️  Port 5000 is already in use!
⚠️  Port 3000 is already in use!
```

**Solution:**
Script tự động free ports. Nếu không work:
```bash
# Manual stop
./stop_webui.sh

# Check ports
lsof -i :5000
lsof -i :3000

# Force kill
kill -9 <PID>
```

---

### **Problem 2: Backend failed to start**

**Symptom:**
```
❌ Backend failed to start!
Check log: cat /tmp/crypto_scanner_backend.log
```

**Solution:**
```bash
# Check log
cat /tmp/crypto_scanner_backend.log

# Common issues:
# 1. Flask not installed
cd web-ui
source venv/bin/activate
pip install flask flask-cors

# 2. Python path wrong
which python3
# Use absolute path in script if needed

# 3. Port permission
# Try different port in server.py
```

---

### **Problem 3: Frontend failed to start**

**Symptom:**
```
❌ Frontend failed to start!
Check log: cat /tmp/crypto_scanner_frontend.log
```

**Solution:**
```bash
# Check log
cat /tmp/crypto_scanner_frontend.log

# Common issues:
# 1. Node modules not installed
cd web-ui
rm -rf node_modules
npm install

# 2. Vite config error
# Check vite.config.js syntax

# 3. Port permission
# Change port in vite.config.js
```

---

### **Problem 4: Services won't stop**

**Symptom:**
```
./stop_webui.sh doesn't kill processes
```

**Solution:**
```bash
# Find and kill manually
ps aux | grep "python.*server.py"
ps aux | grep "vite"

# Kill by PID
kill -9 <PID>

# Force kill all
pkill -f "python.*server.py"
pkill -f "vite.*3000"

# Clear ports
lsof -ti:5000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

---

### **Problem 5: Can't access UI in browser**

**Symptom:**
- Backend running ✅
- Frontend running ✅
- But browser shows "Can't connect"

**Solution:**
```bash
# 1. Check status
./status_webui.sh

# 2. Check if ports actually listening
lsof -i :3000
lsof -i :5000

# 3. Try different browser
# Chrome, Firefox, Safari

# 4. Check firewall
# macOS: System Preferences > Security > Firewall

# 5. Try localhost vs 127.0.0.1
http://localhost:3000
http://127.0.0.1:3000
```

---

## 📋 **WORKFLOW EXAMPLES**

### **Example 1: Normal Usage**

```bash
# Morning - Start UI
./run_webui.sh
# Press Ctrl+C when done

# Or keep running and access anytime
# Open: http://localhost:3000
```

---

### **Example 2: Check if running**

```bash
# Quick check
./status_webui.sh

# If not running, start
./run_webui.sh
```

---

### **Example 3: Restart services**

```bash
# Stop first
./stop_webui.sh

# Wait 2 seconds
sleep 2

# Start again
./run_webui.sh
```

---

### **Example 4: Debug mode**

```bash
# Start with logs visible
./run_webui.sh

# In another terminal, watch logs
tail -f /tmp/crypto_scanner_backend.log
tail -f /tmp/crypto_scanner_frontend.log

# Or use screen/tmux for multi-pane
```

---

## 💡 **PRO TIPS**

### **Tip 1: Alias commands**

Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias webui-start='cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system" && ./run_webui.sh'
alias webui-stop='cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system" && ./stop_webui.sh'
alias webui-status='cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system" && ./status_webui.sh'
```

Then:
```bash
webui-start
webui-status
webui-stop
```

---

### **Tip 2: Auto-start on boot**

Create LaunchAgent (macOS):
```bash
# Create plist file
nano ~/Library/LaunchAgents/com.crypto.scanner.webui.plist
```

Content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.crypto.scanner.webui</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/will208/Desktop/MCP Trading /crypto-trading-system/run_webui.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/com.crypto.scanner.webui.plist
```

---

### **Tip 3: Monitor with watch**

```bash
# Auto-refresh status every 2 seconds
watch -n 2 './status_webui.sh'
```

---

### **Tip 4: Background mode**

```bash
# Start in background (detached)
nohup ./run_webui.sh > /tmp/webui_startup.log 2>&1 &

# Check status
./status_webui.sh

# Stop when needed
./stop_webui.sh
```

---

## 📚 **TÀI LIỆU LIÊN QUAN**

- `web-ui/README.md` - Full Web UI docs
- `web-ui/QUICKSTART.md` - 2-minute start guide
- `docs/WEB_UI_GUIDE.md` - Detailed guide
- `WEB_UI_SUMMARY.md` - Quick overview

---

## 🎯 **SUMMARY**

**3 scripts, 3 mục đích:**

1. **./run_webui.sh** → Start everything
2. **./stop_webui.sh** → Stop everything
3. **./status_webui.sh** → Check status

**Workflow đơn giản:**
```bash
./run_webui.sh          # Start
# Use UI at http://localhost:3000
./stop_webui.sh         # Stop when done
```

**Troubleshooting:**
```bash
./status_webui.sh       # Check what's wrong
cat /tmp/crypto_scanner_backend.log
cat /tmp/crypto_scanner_frontend.log
```

---

**Easy! 🚀💰**
