# 🚀 Crypto Trading Scanner - Web UI

React-based web interface for the Bybit Breakout Strategy Scanner.

## ✨ Features

- 🔍 **One-Click Scanning** - Trigger market scans with a single button
- 📊 **Real-time Dashboard** - Live statistics and signal counts
- 📈 **Signal Table** - Detailed LONG/SHORT signals with entry/exit prices
- 🎯 **Filter Signals** - Filter by ALL/LONG/SHORT
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚡ **Fast & Beautiful** - Modern UI with smooth animations

## 🛠️ Tech Stack

- **Frontend:** React 18 + Vite
- **Backend:** Flask (Python)
- **Styling:** Pure CSS with gradient themes
- **API:** REST API with Flask-CORS

## 📦 Installation

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Virtual environment (included)

### Setup

```bash
# Navigate to web-ui directory
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"

# Install frontend dependencies (already done)
npm install

# Backend dependencies are already installed in venv
```

## 🚀 Running the Application

### Option 1: Separate Terminals (Recommended for Development)

**Terminal 1 - Backend API Server:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
source venv/bin/activate
python server.py
```

The API will run on: `http://localhost:5000`

**Terminal 2 - React Frontend:**
```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
npm run dev
```

The UI will run on: `http://localhost:3000`

### Option 2: Quick Start Script

```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"

# Start backend (Terminal 1)
npm run server

# Start frontend (Terminal 2)
npm run dev
```

### Option 3: Using the Startup Script

```bash
cd "/Users/will208/Desktop/MCP Trading /crypto-trading-system/web-ui"
./start.sh
```

## 📖 Usage

1. **Open Browser:**
   - Navigate to `http://localhost:3000`

2. **Scan Market:**
   - Click the "Scan Now" button
   - Wait 30-60 seconds for scan to complete

3. **View Results:**
   - Dashboard shows summary statistics
   - Table displays all LONG/SHORT signals
   - Filter by direction (ALL/LONG/SHORT)
   - Click on quality scores to understand signal strength

4. **Take Action:**
   - Review signals with Quality Score ≥ 8
   - Note entry prices, targets (TP1, TP2), and stop loss
   - Apply exit strategy: 70% at TP1, 30% at TP2, 6h max hold

## 🎯 Exit Strategy Reminder

The UI displays this reminder with every scan:

```
Hour 3-4: Close 70% at TP1, move SL to breakeven (0%)
Hour 4-6: Close remaining 30% at TP2
Hour 6+:  FORCE CLOSE ALL (prevent reversal!)
```

## 📊 API Endpoints

The backend exposes these endpoints:

- `GET /api/health` - Health check
- `GET /api/config` - Get strategy configuration
- `GET /api/results/latest` - Get latest scan results
- `POST /api/scan` - Trigger new market scan

## 🎨 UI Components

### Dashboard
- Displays scan statistics
- Shows LONG/SHORT signal counts
- Real-time success rate

### Scan Button
- Triggers market scan
- Shows loading state with spinner
- Displays progress message

### Results Table
- Sortable signal table
- Filter by direction
- Quality score badges
- Risk/Reward ratios
- Entry/exit prices

## 🔧 Configuration

### Backend Port (server.py)
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Frontend Port (vite.config.js)
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': 'http://localhost:5000'
  }
}
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Recreate virtual environment
cd web-ui
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

### Frontend build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### No signals showing
- Check if backend is running (`http://localhost:5000/api/health`)
- Verify you're not in dead zone (01:00-08:00 UTC)
- Check console for errors (F12 in browser)

### CORS errors
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Backend must be running on port 5000
- Check browser console for specific CORS error

## 📱 Responsive Breakpoints

- **Desktop:** > 768px (Full table)
- **Tablet:** 480-768px (Simplified table)
- **Mobile:** < 480px (Essential columns only)

## 🎨 Color Scheme

- **Primary Gradient:** #667eea → #764ba2
- **Success (LONG):** #22c55e (Green)
- **Danger (SHORT):** #ef4444 (Red)
- **Background:** White cards on gradient backdrop

## 📈 Expected Performance

- **Scan Time:** 30-60 seconds (84 coins)
- **Page Load:** < 1 second
- **API Response:** < 5 seconds (cached results)

## 🔒 Security Notes

- Backend runs on localhost only (not exposed to internet)
- No authentication required (local use only)
- API keys stored in parent project (not in web-ui)

## 📝 Development Notes

### Adding New Features

1. Backend: Add endpoints to `server.py`
2. Frontend: Create components in `src/components/`
3. Styling: Add CSS in respective `.css` files
4. State: Use React hooks in `App.jsx`

### File Structure
```
web-ui/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── Dashboard.css
│   │   ├── ScanButton.jsx
│   │   ├── ScanButton.css
│   │   ├── ResultsTable.jsx
│   │   └── ResultsTable.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── server.py
├── vite.config.js
├── index.html
├── package.json
└── README.md
```

## 🚀 Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

Production files will be in `dist/` directory.

## 📞 Support

For issues or questions:
1. Check main project documentation: `../docs/README.md`
2. Review strategy guide: `../docs/QUICK_REFERENCE.md`
3. Check backend logs in `../logs/`

## 🎉 Credits

Built for the Crypto Trading System v2.0 - Optimized Exit Strategy (70% at TP1, 6h max hold)

**Happy Trading! 💰🚀**
