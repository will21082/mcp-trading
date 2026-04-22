#!/bin/bash
#
# Auto Crypto Scanner - Optimized Strategy
# Scans Bybit for LONG + SHORT signals with 70% TP1 exit
#
# Usage: ./auto_scan.sh [timeframe]
# Example: ./auto_scan.sh 15m
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Timeframe (default 15m)
TIMEFRAME="${1:-15m}"

# Log directory
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# Report directory
REPORT_DIR="$PROJECT_DIR/reports/scans"
mkdir -p "$REPORT_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_READABLE=$(date +"%Y-%m-%d %H:%M:%S")

# Log files
SCAN_LOG="$LOG_DIR/scan_${TIMESTAMP}.log"
LATEST_LOG="$LOG_DIR/latest_scan.log"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}🔍 CRYPTO AUTO SCANNER - OPTIMIZED STRATEGY${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "Time: ${DATE_READABLE}"
echo -e "Timeframe: ${TIMEFRAME}"
echo -e "Project: ${PROJECT_DIR}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Log header
{
    echo "======================================================================"
    echo "🔍 CRYPTO AUTO SCANNER"
    echo "======================================================================"
    echo "Start Time: ${DATE_READABLE}"
    echo "Timeframe: ${TIMEFRAME}"
    echo "======================================================================"
    echo ""
} > "$SCAN_LOG"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Error: Cannot access project directory${NC}"
    exit 1
}

# Run the scanner
echo -e "${YELLOW}⏳ Running Bybit LONG + SHORT Scanner...${NC}"
echo ""

if uv run python analyzers/bybit_long_short_scanner.py >> "$SCAN_LOG" 2>&1; then
    echo -e "${GREEN}✅ Scan completed successfully!${NC}"

    # Copy to latest log
    cp "$SCAN_LOG" "$LATEST_LOG"

    # Extract results
    LONG_COUNT=$(grep -o "LONG Signals: [0-9]*" "$SCAN_LOG" | grep -o "[0-9]*" || echo "0")
    SHORT_COUNT=$(grep -o "SHORT Signals: [0-9]*" "$SCAN_LOG" | grep -o "[0-9]*" || echo "0")
    TOTAL=$((LONG_COUNT + SHORT_COUNT))

    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${GREEN}📊 RESULTS${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "🟢 LONG Signals:  ${LONG_COUNT}"
    echo -e "🔴 SHORT Signals: ${SHORT_COUNT}"
    echo -e "📊 Total Signals: ${TOTAL}"
    echo -e "${BLUE}======================================================================${NC}"

    if [ "$TOTAL" -gt 0 ]; then
        echo ""
        echo -e "${GREEN}🎉 Found ${TOTAL} trading opportunities!${NC}"
        echo ""
        echo "📄 Full Report:"
        echo "   $REPORT_DIR/BYBIT_LONG_SHORT_OPTIMIZED.md"
        echo ""
        echo "📋 Log File:"
        echo "   $SCAN_LOG"
        echo ""

        # Show top signals from log
        echo -e "${YELLOW}🏆 Top Signals:${NC}"
        echo ""
        grep -A 15 "TOP 5 LONG SIGNALS:" "$SCAN_LOG" 2>/dev/null || true
        grep -A 15 "TOP 5 SHORT SIGNALS:" "$SCAN_LOG" 2>/dev/null || true

    else
        echo ""
        echo -e "${YELLOW}⚠️  No signals found at this time${NC}"
        echo ""
        echo "Possible reasons:"
        echo "  • Market already broke out (post-breakout phase)"
        echo "  • Consolidation phase (waiting for momentum)"
        echo "  • Choppy/ranging market"
        echo ""
        echo "💡 Recommendation:"
        echo "  • Re-scan in 2-4 hours"
        echo "  • Best time: US session open (12:00-16:00 UTC)"
        echo ""
    fi

    # Log completion
    {
        echo ""
        echo "======================================================================"
        echo "✅ SCAN COMPLETED"
        echo "======================================================================"
        echo "End Time: $(date +"%Y-%m-%d %H:%M:%S")"
        echo "Results: ${LONG_COUNT} LONG, ${SHORT_COUNT} SHORT (Total: ${TOTAL})"
        echo "======================================================================"
    } >> "$SCAN_LOG"

else
    echo -e "${RED}❌ Scan failed!${NC}"
    echo ""
    echo "Check log for details:"
    echo "   $SCAN_LOG"
    echo ""

    # Log failure
    {
        echo ""
        echo "======================================================================"
        echo "❌ SCAN FAILED"
        echo "======================================================================"
        echo "End Time: $(date +"%Y-%m-%d %H:%M:%S")"
        echo "Check error details above"
        echo "======================================================================"
    } >> "$SCAN_LOG"

    exit 1
fi

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}✅ Auto Scanner Complete!${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Clean up old logs (keep last 30 days)
find "$LOG_DIR" -name "scan_*.log" -mtime +30 -delete 2>/dev/null || true

exit 0
