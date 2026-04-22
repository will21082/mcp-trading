#!/bin/bash

# ==============================================================================
# Crypto Trading Scanner - Stop Web UI
# ==============================================================================
# This script stops both Flask backend and React frontend
# ==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🛑 Stopping Crypto Scanner Web UI...${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""

STOPPED=0

# Stop using PID files
if [ -f "/tmp/crypto_scanner_backend.pid" ]; then
    BACKEND_PID=$(cat /tmp/crypto_scanner_backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped (PID: $BACKEND_PID)${NC}"
        STOPPED=1
    fi
    rm -f /tmp/crypto_scanner_backend.pid
fi

if [ -f "/tmp/crypto_scanner_frontend.pid" ]; then
    FRONTEND_PID=$(cat /tmp/crypto_scanner_frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped (PID: $FRONTEND_PID)${NC}"
        STOPPED=1
    fi
    rm -f /tmp/crypto_scanner_frontend.pid
fi

# Force kill by port if still running
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Backend still running on port 5000, force stopping...${NC}"
    PID=$(lsof -ti:5000)
    kill -9 $PID 2>/dev/null
    echo -e "${GREEN}✅ Backend force stopped${NC}"
    STOPPED=1
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Frontend still running on port 3000, force stopping...${NC}"
    PID=$(lsof -ti:3000)
    kill -9 $PID 2>/dev/null
    echo -e "${GREEN}✅ Frontend force stopped${NC}"
    STOPPED=1
fi

# Kill any remaining Python server.py processes
PYTHON_PIDS=$(pgrep -f "python.*server.py")
if [ ! -z "$PYTHON_PIDS" ]; then
    echo -e "${YELLOW}⚠️  Found remaining Python processes, stopping...${NC}"
    echo "$PYTHON_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✅ Python processes stopped${NC}"
    STOPPED=1
fi

# Kill any remaining npm/vite processes for this project
NPM_PIDS=$(pgrep -f "vite.*3000")
if [ ! -z "$NPM_PIDS" ]; then
    echo -e "${YELLOW}⚠️  Found remaining Vite processes, stopping...${NC}"
    echo "$NPM_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✅ Vite processes stopped${NC}"
    STOPPED=1
fi

echo ""

if [ $STOPPED -eq 0 ]; then
    echo -e "${BLUE}ℹ️  No running services found${NC}"
else
    echo -e "${GREEN}✨ All services stopped successfully!${NC}"
fi

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""
