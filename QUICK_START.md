# Quick Start - Email Alert System

## TL;DR - Get Running in 1 Hour

### 1. Create Gmail Account (10 min)
```
1. Go to gmail.com
2. Create: yourcompany-ma-alerts@gmail.com
3. Enable 2-step verification
4. Generate App Password
5. Save both credentials
```

### 2. Set Up Top 6 Sites (30 min)
Configure email alerts on:
- BizBuySell.com
- BizQuest.com
- BusinessBroker.net
- BizBen.com
- BusinessBrokerPhoenixAZ.com
- DealStream.com

**Search criteria for all:**
- States: CA, AZ, NV, NM, TX
- Revenue: $1M-$10M
- Cash Flow: $250K+
- Frequency: Weekly

### 3. Configure System (5 min)
```bash
export ALERT_EMAIL_ADDRESS='your-ma-alerts@gmail.com'
export ALERT_EMAIL_PASSWORD='your-app-password'

cd socal-deal-finder
pip install -r requirements.txt
```

### 4. Wait for Emails (1-7 days)
Check your new Gmail inbox for alert emails.

### 5. Run Parser (2 min)
```bash
python email_parser.py
python sheets_uploader.py  # Optional - needs Google credentials
```

### 6. Review Results
Open the generated JSON file or Google Sheet to see curated opportunities!

---

## One-Command Test

Test your email setup is working:

```bash
python test_email_connection.py
```

This will verify:
- ✅ Email credentials work
- ✅ Can connect to Gmail
- ✅ Can see inbox
- ✅ Shows sample of recent emails

---

## Weekly Workflow (30 min/week)

**Every Monday morning:**

```bash
cd socal-deal-finder
python email_parser.py        # Parse last week's alerts
python sheets_uploader.py     # Update spreadsheet
```

**Then review:**
1. Open Google Sheet
2. Sort by "Date Found" (newest first)
3. Review new listings
4. Update Status column
5. Add notes
6. Click URLs for full details

---

## Folder Structure

```
socal-deal-finder/
├── email_parser.py              # Parse email alerts
├── sheets_uploader.py           # Upload to Google Sheets
├── test_email_connection.py     # Test email setup
├── data/
│   └── email_listings_*.json    # Parsed results
└── EMAIL_ALERT_SETUP_GUIDE.md   # Full documentation
```

---

## Environment Variables

Required:
```bash
ALERT_EMAIL_ADDRESS      # Gmail address
ALERT_EMAIL_PASSWORD     # Gmail App Password
```

Optional:
```bash
GOOGLE_CREDENTIALS_PATH  # For Google Sheets integration
GOOGLE_SHEET_NAME        # Sheet name (default: "M&A Opportunities Tracker")
SHEET_SHARE_EMAIL        # Email to share sheet with
```

---

## Troubleshooting

**"Authentication failed"**
→ Use App Password, not regular password
→ Enable 2-step verification first

**"No emails found"**
→ Wait longer (sites send weekly)
→ Check Gmail inbox manually
→ Verify alerts are configured

**"No Google Sheets"**
→ System still saves to JSON
→ Import JSON to Excel manually
→ Or set up Google credentials (see full guide)

---

## What You Get

**Input:** Email alerts from 28 M&A platforms

**Output:** Curated spreadsheet with:
- Business name, location, price
- Revenue and cash flow
- Direct links to listings
- Filterable by state, industry, etc.
- Status tracking
- Notes column

**Result:** 10 hours/week saved. Never miss an opportunity.

---

## Next Steps

1. **Start now**: Create Gmail account
2. **This week**: Set up 6 priority platforms
3. **Next week**: Run first parse, see results
4. **Following week**: Add remaining 22 platforms
5. **Ongoing**: Review 30 min/week

---

## Full Documentation

See `EMAIL_ALERT_SETUP_GUIDE.md` for complete step-by-step instructions.
