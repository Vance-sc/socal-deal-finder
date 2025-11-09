# Email Alert Setup Guide - Complete Walkthrough

This guide will walk you through setting up a **100% FREE** automated M&A deal finder using email alerts.

## Overview

**What we're building:**
1. Dedicated email account receives alerts from 28 M&A platforms
2. Python script parses emails weekly
3. Filtered opportunities uploaded to Google Sheets
4. You review curated list instead of visiting 28 websites

**Cost:** $0/month
**Time to setup:** 2-3 hours (one-time)
**Time saved:** 10+ hours/week forever

---

## Step 1: Create Dedicated Gmail Account (10 minutes)

### Why a dedicated email?
- Keeps M&A alerts separate from personal email
- Easier to parse (only contains deal alerts)
- Can share access with team members

### Create the account:

1. Go to https://accounts.google.com/signup
2. Create new Gmail account
   - Recommended name: `[yourcompany]-ma-alerts@gmail.com`
   - Example: `socalgroup-ma-alerts@gmail.com`
3. Complete signup process
4. Save credentials securely

---

## Step 2: Generate Google App Password (5 minutes)

Gmail requires an "App Password" for programmatic access (not your regular password).

### Steps:

1. **Enable 2-Step Verification** (required for App Passwords)
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow prompts to enable

2. **Create App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it: "M&A Deal Finder"
   - Click "Generate"
   - **SAVE THIS PASSWORD** - you'll need it later
   - It will look like: `abcd efgh ijkl mnop`

---

## Step 3: Set Up Email Alerts on M&A Platforms (2-3 hours)

Now the important part - setting up alerts on all platforms.

### General Process (same for most platforms):

1. Go to platform website
2. Create free account (use your new dedicated email)
3. Find "Alerts" or "Saved Searches" section
4. Configure search criteria
5. Set alert frequency to "Weekly" or "Daily"

### Search Criteria Template

Use these settings on EVERY platform:

**Location/States:**
- California (CA)
- Arizona (AZ)
- Nevada (NV)
- New Mexico (NM)
- Texas (TX)

**Revenue Range:**
- Minimum: $1,000,000
- Maximum: $10,000,000

**Cash Flow/EBITDA:**
- Minimum: $250,000

**Exclude:**
- Restaurants
- Franchises
- Bars
- Food service

**Alert Frequency:**
- Weekly digest (Mondays preferred)
- Or daily for high-priority sites

---

### Platform-by-Platform Setup Guide

#### Priority Sites (Do These First)

**1. BizBuySell** - https://www.bizbuysell.com/
```
1. Create account
2. Go to: Account > Saved Searches & Alerts
3. Click "Create Search Alert"
4. Configure:
   - States: CA, AZ, NV, NM, TX
   - Revenue: $1M - $10M
   - Cash Flow: $250K+
   - Exclude: Restaurants, Franchises
5. Frequency: Weekly
6. Save alert
```

**2. BizQuest** - https://www.bizquest.com/
```
1. Create account
2. Top menu > Email Alerts
3. Build search:
   - Location: Select each state
   - Revenue: $1M-$10M
   - Cash Flow: $250K+
4. Frequency: Weekly
5. Save
```

**3. Business Broker Network** - https://www.businessbroker.net/
```
1. Sign up
2. My Account > Email Alerts
3. Create alert with criteria
4. Weekly frequency
```

**4. BizBen** - https://www.bizben.com/
```
1. Register (use California specialist features)
2. Setup > Email Notifications
3. California-focused search
4. Weekly updates
```

**5. Strategic Business Brokers (Phoenix)** - https://www.businessbrokerphoenixaz.com/
```
1. Create account
2. Contact form > Request alerts
3. Specify: AZ, NV, NM focus
4. Weekly emails
```

**6. DealStream** - https://dealstream.com/
```
1. Free registration
2. My DealStream > Email Preferences
3. Configure search criteria
4. Weekly digest
```

#### Additional Sites (Do These Next)

**7. Sunbelt Business Brokers** - https://www.sunbeltnetwork.com/
**8. MergerNetwork** - https://www.mergernetwork.com/
**9. BusinessesForSale.com** - https://www.businessesforsale.com/
**10. Transworld Business Advisors** - https://www.tworld.com/
**11. Murphy Business** - https://www.murphybusiness.com/
**12. VR Business Brokers** - https://www.vrbbusinessbrokers.com/
**13. Flippa** - https://flippa.com/ (has email alerts + API)
**14. LoopNet** - https://www.loopnet.com/ (commercial real estate focus)
**15. Acquire.com** - https://acquire.com/ (startup focus)
**16. MicroAcquire** - https://microacquire.com/
**17. Empire Flippers** - https://empireflippers.com/
**18. BizEx** - https://www.bizex.net/
**19. BusinessMart** - https://www.businessmart.com/
**20. BizBroker24** - https://www.bizbroker24.com/
**21. BusinessBroker.com** - https://www.businessbroker.com/
**22. BizOffers** - https://www.bizoffers.com/
**23. BuySellBusiness.com** - https://www.buysellbusiness.com/
**24. FE International** - https://feinternational.com/
**25. Quiet Light** - https://quietlight.com/
**26. Axial Network** - https://www.axial.net/ (membership-based)
**27. IBBA** - https://www.ibba.org/
**28. BusinessesForSale.com** (UK/International) - https://www.businessesforsale.com/

### Time-Saving Tips:

- Use a password manager (1Password, LastPass) to save login info
- Copy/paste your criteria to speed up forms
- Do 5-10 sites per day over 3 days
- Some sites may require broker contact - just request email alerts
- Not all sites will have perfect filtering - that's okay, our script handles it

---

## Step 4: Configure the System (15 minutes)

### Set up environment variables:

On your computer (Mac/Linux):

```bash
# Edit your ~/.bashrc or ~/.zshrc
export ALERT_EMAIL_ADDRESS='your-ma-alerts@gmail.com'
export ALERT_EMAIL_PASSWORD='abcd efgh ijkl mnop'  # App password from Step 2
export GOOGLE_SHEET_NAME='M&A Opportunities Tracker'
export SHEET_SHARE_EMAIL='your-work-email@company.com'  # Optional
```

On Windows:
```powershell
setx ALERT_EMAIL_ADDRESS "your-ma-alerts@gmail.com"
setx ALERT_EMAIL_PASSWORD "abcd efgh ijkl mnop"
```

### Install dependencies:

```bash
cd socal-deal-finder
pip install -r requirements.txt
```

---

## Step 5: (Optional) Set Up Google Sheets Integration

For automatic spreadsheet updates, you need a Google service account.

### Steps:

1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable Google Sheets API
   - Go to "APIs & Services" > "Library"
   - Search "Google Sheets API"
   - Click "Enable"
4. Create Service Account
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: "M&A Deal Finder"
   - Click "Create and Continue"
   - Skip role assignment
   - Click "Done"
5. Create Key
   - Click on your new service account
   - Go to "Keys" tab
   - "Add Key" > "Create new key"
   - Choose "JSON"
   - Download file
6. Save credentials
   ```bash
   mv ~/Downloads/service-account-key.json ~/socal-deal-finder/credentials.json
   export GOOGLE_CREDENTIALS_PATH=~/socal-deal-finder/credentials.json
   ```

---

## Step 6: Wait for Emails (1-7 days)

After setting up alerts, you need to wait for emails to arrive.

**Timeline:**
- **Immediate sites**: Some send alerts within hours
- **Daily sites**: Check next day
- **Weekly sites**: Wait until next Monday
- **Best test**: Wait 7 days for full coverage

**What to expect:**
- You should start receiving emails within 24-48 hours
- Weekly digest sites send on Mondays typically
- Some sites send individual listing alerts
- Others send digest emails with multiple listings

---

## Step 7: Run the Parser (5 minutes)

After emails start arriving:

```bash
cd socal-deal-finder

# Parse emails from past 7 days
python email_parser.py

# Upload to Google Sheets (if configured)
python sheets_uploader.py
```

**What happens:**
1. Script connects to your Gmail account
2. Searches for emails from M&A platforms
3. Parses HTML content for listing data
4. Applies your acquisition criteria filters
5. Saves qualified opportunities to JSON
6. (Optional) Uploads to Google Sheets

**Output:**
```
Found 156 total listings from email alerts
Applying filters...
✓ 23 listings meet criteria
✓ Saved to data/email_listings_20251109.json
✓ Uploaded to Google Sheets
```

---

## Step 8: Review Your Curated List

### In Google Sheets:

1. Open the sheet (link provided in output)
2. You'll see columns:
   - Business Name
   - Location (City, State)
   - Asking Price
   - Revenue
   - Cash Flow
   - Industry
   - Source Platform
   - Listing URL (clickable)
   - Status (dropdown)
   - Notes

3. **Features:**
   - ✅ Sortable by any column
   - ✅ Filterable (e.g., show only CA)
   - ✅ Status tracking
   - ✅ Add notes
   - ✅ Share with team

### Workflow:

1. Review new listings weekly
2. Update Status:
   - "New" → "Reviewing"
   - "Reviewing" → "Contacted"
   - "Contacted" → "In Discussion"
   - Or "Pass" if not interested
3. Add notes for follow-up
4. Click URL to view full listing

---

## Step 9: Automate Weekly Runs (Optional)

### On your computer (Mac/Linux):

Create a weekly cron job:

```bash
crontab -e
```

Add this line (runs every Monday at 8am):

```
0 8 * * 1 cd /path/to/socal-deal-finder && python email_parser.py && python sheets_uploader.py
```

### Or on Google Cloud Run:

Deploy the email parser to run on Cloud Scheduler (see main README.md for deployment).

---

## Troubleshooting

### "Authentication failed"
- Check email address and app password are correct
- Make sure you're using App Password, not regular password
- Verify 2-step verification is enabled

### "No emails found"
- Wait longer - some sites only send weekly
- Check your Gmail inbox manually to verify emails arrived
- Check spam folder
- Verify alerts are set up correctly on platforms

### "No Google Sheets credentials"
- System will still save to JSON (can import manually)
- Follow Step 5 to set up Google Sheets integration
- Or just use Excel: Import the JSON file

### "Parsing errors"
- Email formats vary by platform
- Some listings may not parse perfectly
- That's okay - you still get the listing URL to click

### Emails in wrong folder
- All alerts should go to Inbox
- Script searches Inbox by default
- Create filter in Gmail if needed

---

## Maintenance

### Weekly (5 minutes):
- Review new listings in Google Sheets
- Update statuses
- Add notes

### Monthly (15 minutes):
- Check all 28 platforms are still sending alerts
- Update any changed passwords
- Review criteria if needed

### Quarterly (30 minutes):
- Audit which platforms provide best leads
- Adjust alert criteria based on market
- Consider adding new platforms

---

## Expected Results

### After 1 week:
- 20-50 new listings per week
- 5-15 qualified opportunities meeting criteria
- 2-5 highly promising leads

### After 1 month:
- 80-200 total listings reviewed
- 20-60 qualified opportunities
- 10+ leads in discussion
- Possibly 1-2 serious acquisition targets

### Time Saved:
- **Before**: 10+ hours/week manually searching 28 sites
- **After**: 30 minutes/week reviewing curated list
- **Savings**: 9.5 hours/week = 494 hours/year

---

## Cost Analysis

### Setup time:
- Gmail account: 10 min
- App password: 5 min
- Email alerts (28 sites): 2-3 hours (one-time)
- System config: 15 min
- **Total: ~3.5 hours one-time**

### Ongoing time:
- Weekly review: 30 min
- Monthly maintenance: 15 min
- **Total: ~3 hours/month vs. 40+ hours manually**

### Cost:
- **$0/month** (100% free)

---

## Pro Tips

1. **Stagger your alert days**
   - Set some sites to Monday, some to Wednesday
   - Spreads out email load
   - More frequent opportunities

2. **Create Gmail filters**
   - Auto-label emails by platform
   - Easier to track which sites are active
   - Example: Label "BizBuySell" for all from bizbuysell.com

3. **Use the Notes column**
   - Track why you passed on listings
   - Build institutional knowledge
   - Reference for future similar opportunities

4. **Share the sheet**
   - Invite team members
   - Assign listings for review
   - Track who's working on what

5. **Export monthly**
   - Download historical data
   - Track market trends
   - Analyze what types of deals appear

---

## Next Steps

1. ✅ Create dedicated Gmail account
2. ✅ Generate App Password
3. ✅ Set up alerts on 6 priority platforms
4. ⏳ Wait 1-2 days for first emails
5. ✅ Test email_parser.py
6. ✅ Review results
7. ✅ Set up remaining 22 platforms
8. ✅ Automate weekly runs

---

## Support

If you run into issues:
- Check the troubleshooting section above
- Review error messages carefully
- Test with just 1-2 platforms first
- Verify email credentials are correct

---

**You're ready to start!** Set up that Gmail account and start configuring alerts. In 1 week, you'll have a curated list of M&A opportunities delivered automatically.
