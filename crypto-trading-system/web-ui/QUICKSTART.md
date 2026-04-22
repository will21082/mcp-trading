# ⚡ QUICKSTART - Web UI

Get the Web UI running in 2 minutes!

## 🚀 Super Quick Start

```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
./start.sh
```

Then open: `http://localhost:3000` 🎉

## 📋 Manual Start (2 Terminals)

### Terminal 1 - Backend:
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
source venv/bin/activate
python server.py
```

### Terminal 2 - Frontend:
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
npm run dev
```

## 🎯 What You'll See

1. **Dashboard** - Real-time scan statistics
2. **Scan Button** - Click to scan market (30-60s)
3. **Results Table** - All LONG/SHORT signals
4. **Filter** - Toggle between ALL/LONG/SHORT

## 💡 Usage

1. Click "Scan Now"
2. Wait 30-60 seconds
3. Review signals with Quality ≥ 8
4. Apply exit strategy:
   - 70% at TP1 (3-4h)
   - 30% at TP2 (4-6h)
   - Force close at 6h max

## 🐛 Issues?

**Backend won't start:**
```bash
cd web-ui
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

**Frontend errors:**
```bash
cd web-ui
rm -rf node_modules
npm install
```

**No signals:**
- You might be in dead zone (01:00-08:00 UTC)
- Best times: 17:00, 21:00, 01:00 JST

## 📖 Full Documentation

See `README.md` in this directory for complete guide.

---

**Happy Trading! 🚀💰**
