#!/bin/bash

# Startup script for Crypto Trading Scanner Web UI

echo "🚀 Starting Crypto Trading Scanner Web UI..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}📂 Working directory:${NC} $SCRIPT_DIR"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    echo ""
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}🔧 Starting Backend API Server...${NC}"
    source venv/bin/activate
    python server.py &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    echo -e "${GREEN}   API: http://localhost:5000${NC}"
    echo ""
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting React Frontend...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo -e "${GREEN}   UI: http://localhost:3000${NC}"
    echo ""
}

# Start both services
start_backend
sleep 2
start_frontend

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Crypto Scanner UI is READY!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 Backend API:${NC}  http://localhost:5000"
echo -e "${BLUE}⚛️  Frontend UI:${NC}  http://localhost:3000"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Keep script running
wait
