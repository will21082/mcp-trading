#!/bin/bash

# ==============================================================================
# Crypto Trading Scanner - Web UI Launcher
# ==============================================================================
# This script starts both Flask backend and React frontend in one command
# ==============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_UI_DIR="$SCRIPT_DIR/web-ui"

# Clear screen
clear

# Header
echo -e "${PURPLE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                                ║${NC}"
echo -e "${PURPLE}║        ${CYAN}🚀 CRYPTO TRADING SCANNER - WEB UI LAUNCHER${PURPLE}        ║${NC}"
echo -e "${PURPLE}║                                                                ║${NC}"
echo -e "${PURPLE}║             Bybit Breakout Strategy - 15m Timeframe            ║${NC}"
echo -e "${PURPLE}║                                                                ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if web-ui directory exists
if [ ! -d "$WEB_UI_DIR" ]; then
    echo -e "${RED}❌ Error: web-ui directory not found!${NC}"
    echo -e "${YELLOW}Expected location: $WEB_UI_DIR${NC}"
    exit 1
fi

cd "$WEB_UI_DIR"

echo -e "${BLUE}📂 Working directory:${NC} $WEB_UI_DIR"
echo ""

# ==============================================================================
# Check Prerequisites
# ==============================================================================

echo -e "${CYAN}🔍 Checking prerequisites...${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ Python:${NC} $PYTHON_VERSION"
else
    echo -e "${RED}❌ Python 3 not found!${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo -e "${GREEN}✅ Node.js:${NC} $NODE_VERSION"
else
    echo -e "${RED}❌ Node.js not found!${NC}"
    echo -e "${YELLOW}Please install Node.js: https://nodejs.org/${NC}"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version 2>&1)
    echo -e "${GREEN}✅ npm:${NC} v$NPM_VERSION"
else
    echo -e "${RED}❌ npm not found!${NC}"
    exit 1
fi

echo ""

# ==============================================================================
# Setup Virtual Environment (if needed)
# ==============================================================================

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet flask flask-cors
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    echo ""
fi

# ==============================================================================
# Setup Node Modules (if needed)
# ==============================================================================

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    npm install --silent
    echo -e "${GREEN}✅ Node modules installed${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Node modules found${NC}"
    echo ""
fi

# ==============================================================================
# Check if ports are available
# ==============================================================================

echo -e "${CYAN}🔌 Checking ports...${NC}"
echo ""

# Check port 5000 (Backend)
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 5000 is already in use!${NC}"
    echo -e "${YELLOW}Attempting to free port 5000...${NC}"
    PID=$(lsof -ti:5000)
    kill -9 $PID 2>/dev/null
    sleep 1
    echo -e "${GREEN}✅ Port 5000 freed${NC}"
else
    echo -e "${GREEN}✅ Port 5000 available${NC}"
fi

# Check port 3000 (Frontend)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use!${NC}"
    echo -e "${YELLOW}Attempting to free port 3000...${NC}"
    PID=$(lsof -ti:3000)
    kill -9 $PID 2>/dev/null
    sleep 1
    echo -e "${GREEN}✅ Port 3000 freed${NC}"
else
    echo -e "${GREEN}✅ Port 3000 available${NC}"
fi

echo ""

# ==============================================================================
# Start Backend (Flask)
# ==============================================================================

echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🔧 Starting Backend API Server...${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Activate virtual environment and start Flask in background
source venv/bin/activate
python server.py > /tmp/crypto_scanner_backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend started successfully!${NC}"
    echo -e "${GREEN}   PID:${NC} $BACKEND_PID"
    echo -e "${GREEN}   URL:${NC} http://localhost:5000"
    echo -e "${GREEN}   Log:${NC} /tmp/crypto_scanner_backend.log"
else
    echo -e "${RED}❌ Backend failed to start!${NC}"
    echo -e "${YELLOW}Check log: cat /tmp/crypto_scanner_backend.log${NC}"
    exit 1
fi

echo ""

# ==============================================================================
# Start Frontend (React)
# ==============================================================================

echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}⚛️  Starting React Frontend...${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Start React in background
npm run dev > /tmp/crypto_scanner_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend started successfully!${NC}"
    echo -e "${GREEN}   PID:${NC} $FRONTEND_PID"
    echo -e "${GREEN}   URL:${NC} http://localhost:3000"
    echo -e "${GREEN}   Log:${NC} /tmp/crypto_scanner_frontend.log"
else
    echo -e "${RED}❌ Frontend failed to start!${NC}"
    echo -e "${YELLOW}Check log: cat /tmp/crypto_scanner_frontend.log${NC}"
    # Kill backend if frontend fails
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""

# ==============================================================================
# Success Message
# ==============================================================================

echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ WEB UI IS READY! ✨${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}🌐 Access the application:${NC}"
echo ""
echo -e "   ${YELLOW}Frontend UI:${NC}  ${BLUE}http://localhost:3000${NC}  ⭐ Open this!"
echo -e "   ${YELLOW}Backend API:${NC}  ${BLUE}http://localhost:5000${NC}"
echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📊 How to use:${NC}"
echo -e "   1. Open ${BLUE}http://localhost:3000${NC} in your browser"
echo -e "   2. Click ${YELLOW}\"🔍 Scan Now\"${NC} button"
echo -e "   3. Wait 30-60 seconds for scan to complete"
echo -e "   4. Review signals in dashboard and table"
echo -e "   5. Trade on signals with Quality ≥ 8"
echo ""
echo -e "${CYAN}⚡ Exit Strategy:${NC}"
echo -e "   • Hour 3-4: Close ${GREEN}70%${NC} at TP1, move SL to breakeven"
echo -e "   • Hour 4-6: Close remaining ${GREEN}30%${NC} at TP2"
echo -e "   • Hour 6+:  ${RED}FORCE CLOSE ALL${NC} (prevent reversal!)"
echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📝 Process IDs:${NC}"
echo -e "   Backend:  ${BACKEND_PID}"
echo -e "   Frontend: ${FRONTEND_PID}"
echo ""
echo -e "${CYAN}📋 Logs:${NC}"
echo -e "   Backend:  tail -f /tmp/crypto_scanner_backend.log"
echo -e "   Frontend: tail -f /tmp/crypto_scanner_frontend.log"
echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop both services${NC}"
echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Save PIDs to file for cleanup script
echo "$BACKEND_PID" > /tmp/crypto_scanner_backend.pid
echo "$FRONTEND_PID" > /tmp/crypto_scanner_frontend.pid

# ==============================================================================
# Cleanup Handler
# ==============================================================================

cleanup() {
    echo ""
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    echo ""

    # Kill backend
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped (PID: $BACKEND_PID)${NC}"
    fi

    # Kill frontend
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped (PID: $FRONTEND_PID)${NC}"
    fi

    # Clean up PID files
    rm -f /tmp/crypto_scanner_backend.pid
    rm -f /tmp/crypto_scanner_frontend.pid

    echo ""
    echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}👋 Web UI stopped. Happy trading!${NC}"
    echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
    echo ""

    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# ==============================================================================
# Keep Script Running
# ==============================================================================

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
