#!/bin/bash
# Weekly M&A Deal Parser for SoCal Business Group (OAuth Version)
# Run this every Monday to get your curated list

set -e

echo "======================================================================"
echo "SoCal Business Group - M&A Deal Finder"
echo "Weekly Alert Parser (Google OAuth)"
echo "======================================================================"
echo ""

# Load .env if exists
if [ -f .env ]; then
    echo "✓ Loading configuration from .env"
    export $(cat .env | grep -v '^#' | xargs)
    echo ""
fi

# Check for OAuth credentials
if [ ! -f "${GOOGLE_OAUTH_CREDENTIALS:-oauth_credentials.json}" ]; then
    echo "❌ ERROR: OAuth credentials not found"
    echo ""
    echo "Please set up Google OAuth first:"
    echo "  1. Follow instructions in OAUTH_SETUP_GUIDE.md"
    echo "  2. Download oauth_credentials.json from Google Cloud Console"
    echo "  3. Save it in this directory"
    echo ""
    exit 1
fi

echo "Configuration:"
echo "  Email: ${ALERT_EMAIL_ADDRESS:-vance@socalbusinessgroup.com}"
echo "  Alias: ${ALERT_EMAIL_ALIAS:-biz-search@socalbusinessgroup.com}"
echo "  OAuth: ${GOOGLE_OAUTH_CREDENTIALS:-oauth_credentials.json}"
echo ""

# Check if first run (no token)
if [ ! -f "token.pickle" ]; then
    echo "🔐 FIRST RUN - OAuth Authentication Required"
    echo "A browser window will open for you to sign in with Google"
    echo "After signing in once, future runs will be automatic"
    echo ""
fi

# Run the OAuth parser
echo "Step 1: Parsing email alerts (OAuth)..."
echo "----------------------------------------------------------------------"
python email_parser_oauth.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Email parsing failed"
    echo ""
    echo "Common issues:"
    echo "  1. OAuth not set up - see OAUTH_SETUP_GUIDE.md"
    echo "  2. Browser didn't open - check firewall"
    echo "  3. Wrong Google account - use vance@socalbusinessgroup.com"
    exit 1
fi

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
echo "Token stored in token.pickle - future runs won't need browser"
echo ""
echo "Have a great week finding deals!"
echo ""
