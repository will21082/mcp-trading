#!/bin/bash

# ==============================================================================
# Crypto Trading Scanner - Web UI Status Check
# ==============================================================================
# This script checks the status of backend and frontend services
# ==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}📊 Crypto Scanner Web UI - Status Check${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# ==============================================================================
# Check Backend (Port 5000)
# ==============================================================================

echo -e "${CYAN}🔧 Backend API (Flask):${NC}"
echo ""

if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PID=$(lsof -ti:5000)
    echo -e "   Status:  ${GREEN}✅ RUNNING${NC}"
    echo -e "   PID:     ${GREEN}$PID${NC}"
    echo -e "   Port:    ${GREEN}5000${NC}"
    echo -e "   URL:     ${BLUE}http://localhost:5000${NC}"

    # Test API health
    if command -v curl &> /dev/null; then
        HEALTH=$(curl -s http://localhost:5000/api/health 2>/dev/null)
        if [ ! -z "$HEALTH" ]; then
            echo -e "   Health:  ${GREEN}✅ API responding${NC}"
        else
            echo -e "   Health:  ${YELLOW}⚠️  Port open but API not responding${NC}"
        fi
    fi
else
    echo -e "   Status:  ${RED}❌ NOT RUNNING${NC}"
    echo -e "   Port:    ${RED}5000 (not listening)${NC}"
fi

echo ""

# ==============================================================================
# Check Frontend (Port 3000)
# ==============================================================================

echo -e "${CYAN}⚛️  Frontend (React):${NC}"
echo ""

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PID=$(lsof -ti:3000)
    echo -e "   Status:  ${GREEN}✅ RUNNING${NC}"
    echo -e "   PID:     ${GREEN}$PID${NC}"
    echo -e "   Port:    ${GREEN}3000${NC}"
    echo -e "   URL:     ${BLUE}http://localhost:3000${NC}"

    # Test frontend
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "   Health:  ${GREEN}✅ UI accessible${NC}"
        else
            echo -e "   Health:  ${YELLOW}⚠️  Port open but UI not fully loaded (HTTP $HTTP_CODE)${NC}"
        fi
    fi
else
    echo -e "   Status:  ${RED}❌ NOT RUNNING${NC}"
    echo -e "   Port:    ${RED}3000 (not listening)${NC}"
fi

echo ""

# ==============================================================================
# Overall Status
# ==============================================================================

BACKEND_UP=0
FRONTEND_UP=0

if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    BACKEND_UP=1
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    FRONTEND_UP=1
fi

echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ $BACKEND_UP -eq 1 ] && [ $FRONTEND_UP -eq 1 ]; then
    echo -e "${GREEN}✨ Overall Status: ${GREEN}FULLY OPERATIONAL${NC}"
    echo ""
    echo -e "   ${CYAN}🌐 Access the UI:${NC} ${BLUE}http://localhost:3000${NC}"
    echo ""
elif [ $BACKEND_UP -eq 1 ] || [ $FRONTEND_UP -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Overall Status: ${YELLOW}PARTIALLY RUNNING${NC}"
    echo ""
    if [ $BACKEND_UP -eq 0 ]; then
        echo -e "   ${RED}❌ Backend not running${NC}"
    fi
    if [ $FRONTEND_UP -eq 0 ]; then
        echo -e "   ${RED}❌ Frontend not running${NC}"
    fi
    echo ""
    echo -e "   ${CYAN}To start:${NC} ./run_webui.sh"
    echo ""
else
    echo -e "${RED}❌ Overall Status: ${RED}NOT RUNNING${NC}"
    echo ""
    echo -e "   ${CYAN}To start:${NC} ./run_webui.sh"
    echo ""
fi

# ==============================================================================
# Process Information
# ==============================================================================

echo -e "${CYAN}📋 Process Details:${NC}"
echo ""

# Python processes
PYTHON_PROCS=$(ps aux | grep "[p]ython.*server.py" | awk '{print $2, $11, $12, $13}')
if [ ! -z "$PYTHON_PROCS" ]; then
    echo -e "   ${YELLOW}Python (server.py):${NC}"
    echo "$PYTHON_PROCS" | while read line; do
        echo -e "      PID: $line"
    done
    echo ""
fi

# Vite/Node processes
VITE_PROCS=$(ps aux | grep "[v]ite" | grep "3000" | awk '{print $2, $11, $12, $13}')
if [ ! -z "$VITE_PROCS" ]; then
    echo -e "   ${YELLOW}Vite (React):${NC}"
    echo "$VITE_PROCS" | while read line; do
        echo -e "      PID: $line"
    done
    echo ""
fi

if [ -z "$PYTHON_PROCS" ] && [ -z "$VITE_PROCS" ]; then
    echo -e "   ${BLUE}No Web UI processes running${NC}"
    echo ""
fi

# ==============================================================================
# Logs
# ==============================================================================

echo -e "${CYAN}📄 Log Files:${NC}"
echo ""

if [ -f "/tmp/crypto_scanner_backend.log" ]; then
    SIZE=$(ls -lh /tmp/crypto_scanner_backend.log | awk '{print $5}')
    echo -e "   Backend:  ${GREEN}/tmp/crypto_scanner_backend.log${NC} ($SIZE)"
else
    echo -e "   Backend:  ${BLUE}No log file${NC}"
fi

if [ -f "/tmp/crypto_scanner_frontend.log" ]; then
    SIZE=$(ls -lh /tmp/crypto_scanner_frontend.log | awk '{print $5}')
    echo -e "   Frontend: ${GREEN}/tmp/crypto_scanner_frontend.log${NC} ($SIZE)"
else
    echo -e "   Frontend: ${BLUE}No log file${NC}"
fi

echo ""

# ==============================================================================
# Quick Actions
# ==============================================================================

echo -e "${CYAN}⚡ Quick Actions:${NC}"
echo ""
echo -e "   Start:    ${YELLOW}./run_webui.sh${NC}"
echo -e "   Stop:     ${YELLOW}./stop_webui.sh${NC}"
echo -e "   Status:   ${YELLOW}./status_webui.sh${NC}"
echo ""
echo -e "   Logs:     ${YELLOW}tail -f /tmp/crypto_scanner_backend.log${NC}"
echo -e "             ${YELLOW}tail -f /tmp/crypto_scanner_frontend.log${NC}"
echo ""

echo -e "${PURPLE}════════════════════════════════════════════════════════════════${NC}"
echo ""
