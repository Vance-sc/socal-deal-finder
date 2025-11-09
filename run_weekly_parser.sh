#!/bin/bash
# Weekly M&A Deal Parser for SoCal Business Group
# Run this every Monday to get your curated list

set -e

echo "======================================================================"
echo "SoCal Business Group - M&A Deal Finder"
echo "Weekly Alert Parser"
echo "======================================================================"
echo ""

# Check environment variables
if [ -z "$ALERT_EMAIL_ADDRESS" ]; then
    echo "❌ ERROR: Email credentials not configured"
    echo ""
    echo "Please set up your .env file first:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your credentials"
    echo ""
    echo "Or set environment variables:"
    echo "  export ALERT_EMAIL_ADDRESS='vance@socalbusinessgroup.com'"
    echo "  export ALERT_EMAIL_PASSWORD='your-app-password'"
    echo "  export ALERT_EMAIL_ALIAS='biz-search@socalbusinessgroup.com'"
    exit 1
fi

# Load .env if exists
if [ -f .env ]; then
    echo "✓ Loading configuration from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Configuration:"
echo "  Main email: $ALERT_EMAIL_ADDRESS"
echo "  Alias email: ${ALERT_EMAIL_ALIAS:-$ALERT_EMAIL_ADDRESS}"
echo ""

# Run the alias-optimized parser
echo "Step 1: Parsing email alerts..."
echo "----------------------------------------------------------------------"
python email_parser_alias.py

echo ""
echo "Step 2: Uploading to Google Sheets..."
echo "----------------------------------------------------------------------"
python sheets_uploader.py || echo "⚠ Google Sheets upload skipped (credentials not configured)"

echo ""
echo "======================================================================"
echo "✓ COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Review data/email_listings_*.json"
echo "  2. Open your Google Sheet (if uploaded)"
echo "  3. Update statuses and add notes"
echo "  4. Click listing URLs to investigate opportunities"
echo ""
echo "Have a great week finding deals!"
echo ""
