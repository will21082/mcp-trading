#!/bin/bash
#
# Send Email Notification with Scan Results
# Optional: Configure this to receive email alerts
#
# Prerequisites:
# - Install mail utility: brew install mailutils (macOS)
# - Or use sendmail, or external service like SendGrid
#

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
LATEST_LOG="$PROJECT_DIR/logs/latest_scan.log"
REPORT_FILE="$PROJECT_DIR/reports/scans/BYBIT_LONG_SHORT_OPTIMIZED.md"

# ============================================
# CONFIGURATION - EDIT THESE!
# ============================================

# Your email address
TO_EMAIL="hoangnguyenanh2108@gmail.com"

# From email (can be same as TO_EMAIL)
FROM_EMAIL="crypto-scanner@yourdomain.com"

# Email subject
SUBJECT="🔍 Crypto Scan Results - $(date +"%Y-%m-%d %H:%M")"

# SMTP settings (if using external service like Gmail, SendGrid, etc.)
# SMTP_SERVER="smtp.gmail.com"
# SMTP_PORT="587"
# SMTP_USER="your-email@gmail.com"
# SMTP_PASS="your-app-password"

# ============================================
# END CONFIGURATION
# ============================================

# Check if log exists
if [ ! -f "$LATEST_LOG" ]; then
    echo "❌ No scan results found!"
    exit 1
fi

# Extract results
LONG_COUNT=$(grep -o "LONG Signals: [0-9]*" "$LATEST_LOG" | grep -o "[0-9]*" || echo "0")
SHORT_COUNT=$(grep -o "SHORT Signals: [0-9]*" "$LATEST_LOG" | grep -o "[0-9]*" || echo "0")
TOTAL=$((LONG_COUNT + SHORT_COUNT))

# Create email body
EMAIL_BODY=$(cat <<EOF
Crypto Auto Scan Results
========================

Date: $(date +"%Y-%m-%d %H:%M:%S")
Exchange: BYBIT
Timeframe: 15M
Strategy: Breakout (OPTIMIZED - 70% at TP1, 6h max)

RESULTS:
--------
🟢 LONG Signals:  ${LONG_COUNT}
🔴 SHORT Signals: ${SHORT_COUNT}
📊 Total Signals: ${TOTAL}

EOF
)

if [ "$TOTAL" -gt 0 ]; then
    EMAIL_BODY+=$(cat <<EOF

🎉 Found ${TOTAL} trading opportunities!

TOP SIGNALS:
-----------
$(grep -A 20 "TOP 5 LONG SIGNALS:" "$LATEST_LOG" 2>/dev/null || echo "No LONG signals")

$(grep -A 20 "TOP 5 SHORT SIGNALS:" "$LATEST_LOG" 2>/dev/null || echo "No SHORT signals")

FULL REPORT:
-----------
See attached or check: $REPORT_FILE

REMEMBER:
--------
✅ Close 70% at TP1 (3-4 hours)
✅ Move SL to breakeven after TP1
✅ Force exit at 6 hours max
✅ Expected win rate: 75-80%

Good luck! 🚀
EOF
)
else
    EMAIL_BODY+=$(cat <<EOF

⚠️  No signals found at this time

Possible reasons:
• Market already broke out (post-breakout phase)
• Consolidation phase (waiting for momentum)
• Choppy/ranging market

💡 Recommendation:
• Wait for next scan
• Best time: US session open (12:00-16:00 UTC)

Next scan in a few hours! 📊
EOF
)
fi

# ============================================
# SEND EMAIL
# ============================================

# METHOD 1: Using macOS mail command (simple)
echo "$EMAIL_BODY" | mail -s "$SUBJECT" "$TO_EMAIL" 2>/dev/null

# METHOD 2: Using sendmail (alternative)
# {
#     echo "To: $TO_EMAIL"
#     echo "From: $FROM_EMAIL"
#     echo "Subject: $SUBJECT"
#     echo ""
#     echo "$EMAIL_BODY"
# } | sendmail -t

# METHOD 3: Using external service (SendGrid, Mailgun, etc.)
# Implement API call here if using external service

# METHOD 4: Using Python (if mail command not available)
# python3 << EOF
# import smtplib
# from email.mime.text import MIMEText
#
# msg = MIMEText("""$EMAIL_BODY""")
# msg['Subject'] = "$SUBJECT"
# msg['From'] = "$FROM_EMAIL"
# msg['To'] = "$TO_EMAIL"
#
# # For Gmail - use app password, not regular password!
# # server = smtplib.SMTP('smtp.gmail.com', 587)
# # server.starttls()
# # server.login("$SMTP_USER", "$SMTP_PASS")
# # server.send_message(msg)
# # server.quit()
#
# print("Email sent!")
# EOF

if [ $? -eq 0 ]; then
    echo "✅ Email sent to $TO_EMAIL"
else
    echo "⚠️  Email sending failed. Check configuration."
    echo ""
    echo "📝 Email Preview:"
    echo "================="
    echo "$EMAIL_BODY"
    echo "================="
fi
