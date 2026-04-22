#!/bin/bash
#
# Setup Cron Jobs for Auto Crypto Scanner
# Run this script ONCE to install cron jobs
#

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}⏰ SETUP AUTOMATED CRYPTO SCANNING${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Get project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
AUTO_SCAN_SCRIPT="$SCRIPT_DIR/auto_scan.sh"

echo "Project Directory: $PROJECT_DIR"
echo "Auto Scan Script: $AUTO_SCAN_SCRIPT"
echo ""

# Check if auto_scan.sh exists
if [ ! -f "$AUTO_SCAN_SCRIPT" ]; then
    echo -e "${RED}❌ Error: auto_scan.sh not found!${NC}"
    exit 1
fi

# Make sure it's executable
chmod +x "$AUTO_SCAN_SCRIPT"

echo -e "${YELLOW}📋 Proposed Cron Schedule:${NC}"
echo ""
echo "┌─────────────────────────────────────────────────────────────────────┐"
echo "│ Time (Local) │ UTC Time │ Session      │ Description              │"
echo "├─────────────────────────────────────────────────────────────────────┤"
echo "│ 08:00 AM     │ 00:00    │ Asia         │ Night/Early Morning      │"
echo "│ 02:00 PM     │ 06:00    │ EU           │ EU Session Open          │"
echo "│ 08:00 PM     │ 12:00    │ US           │ US Session Open (BEST!)  │"
echo "│ 02:00 AM     │ 18:00    │ Late US      │ US Session Close         │"
echo "└─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "Note: Times shown are examples. Adjust based on your timezone."
echo ""

# Get current timezone
TIMEZONE=$(date +%Z)
echo "Current Timezone: $TIMEZONE"
echo ""

echo -e "${YELLOW}🎯 Recommended Setup (4 scans/day):${NC}"
echo ""
echo "Option 1 - BEST (High frequency, catch all sessions):"
echo "  • 08:00 - Morning scan (Asia + EU overlap)"
echo "  • 14:00 - Afternoon scan (EU + US overlap) ⭐ BEST TIME!"
echo "  • 20:00 - Evening scan (US close)"
echo "  • 02:00 - Night scan (Asia session)"
echo ""
echo "Option 2 - MODERATE (2 scans/day):"
echo "  • 08:00 - Morning scan"
echo "  • 14:00 - Afternoon scan (US open - highest volume!)"
echo ""
echo "Option 3 - MINIMAL (1 scan/day):"
echo "  • 14:00 - US open (single best time)"
echo ""

# Ask user which option
echo -e "${BLUE}Which option do you want?${NC}"
echo "1) Option 1 - 4 scans/day (recommended)"
echo "2) Option 2 - 2 scans/day"
echo "3) Option 3 - 1 scan/day"
echo "4) Custom schedule"
echo "5) View current crontab (no changes)"
echo "0) Cancel"
echo ""
read -p "Enter choice [1-5, 0 to cancel]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}✅ Setting up Option 1: 4 scans/day${NC}"
        CRON_LINES=(
            "0 8 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Morning scan"
            "0 14 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Afternoon scan (BEST!)"
            "0 20 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Evening scan"
            "0 2 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Night scan"
        )
        ;;
    2)
        echo ""
        echo -e "${GREEN}✅ Setting up Option 2: 2 scans/day${NC}"
        CRON_LINES=(
            "0 8 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Morning scan"
            "0 14 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Afternoon scan (BEST!)"
        )
        ;;
    3)
        echo ""
        echo -e "${GREEN}✅ Setting up Option 3: 1 scan/day${NC}"
        CRON_LINES=(
            "0 14 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1  # Daily scan at US open"
        )
        ;;
    4)
        echo ""
        echo -e "${YELLOW}Custom schedule selected${NC}"
        echo "Please edit crontab manually: crontab -e"
        echo ""
        echo "Example cron line:"
        echo "0 14 * * * $AUTO_SCAN_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"
        echo ""
        exit 0
        ;;
    5)
        echo ""
        echo -e "${BLUE}Current crontab:${NC}"
        crontab -l 2>/dev/null || echo "No crontab installed"
        echo ""
        exit 0
        ;;
    0)
        echo ""
        echo "Cancelled."
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Create backup of current crontab
echo ""
echo "📦 Backing up current crontab..."
crontab -l > "$PROJECT_DIR/crontab.backup" 2>/dev/null || touch "$PROJECT_DIR/crontab.backup"
echo "   Saved to: $PROJECT_DIR/crontab.backup"

# Add new cron jobs
echo ""
echo "➕ Adding new cron jobs..."

{
    # Keep existing crontab
    crontab -l 2>/dev/null || true

    # Add header
    echo ""
    echo "# =========================================="
    echo "# Crypto Auto Scanner - Optimized Strategy"
    echo "# Added: $(date)"
    echo "# =========================================="

    # Add cron lines
    for line in "${CRON_LINES[@]}"; do
        echo "$line"
    done

} | crontab -

echo ""
echo -e "${GREEN}✅ Cron jobs installed successfully!${NC}"
echo ""

echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}📋 INSTALLATION COMPLETE${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo "Your scans are now scheduled:"
echo ""

# Show what was installed
for line in "${CRON_LINES[@]}"; do
    echo "  $line"
done

echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
echo "1. ✅ Cron jobs are now active!"
echo "2. 📧 Configure email notifications (optional):"
echo "   Edit: $PROJECT_DIR/scripts/send_email.sh"
echo ""
echo "3. 📊 Check logs:"
echo "   Latest: $PROJECT_DIR/logs/latest_scan.log"
echo "   All logs: $PROJECT_DIR/logs/scan_*.log"
echo "   Cron log: $PROJECT_DIR/logs/cron.log"
echo ""
echo "4. 🧪 Test now (optional):"
echo "   $AUTO_SCAN_SCRIPT"
echo ""
echo "5. 👀 View active cron jobs:"
echo "   crontab -l"
echo ""
echo "6. 🗑️  Remove cron jobs (if needed):"
echo "   crontab -e"
echo "   (Delete the lines under 'Crypto Auto Scanner')"
echo ""

echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}🎉 HAPPY TRADING!${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo "Remember: New strategy = 70% at TP1 (3-4h), breakeven SL, 6h max hold!"
echo "Expected: 75-80% win rate! 🚀"
echo ""
