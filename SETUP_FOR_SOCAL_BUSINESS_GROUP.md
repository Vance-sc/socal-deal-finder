# Setup Guide for SoCal Business Group Email Configuration

## Your Email Setup

**Main Account:** vance@socalbusinessgroup.com
**M&A Alert Alias:** biz-search@socalbusinessgroup.com

This is a great setup! All M&A alerts will arrive in your main inbox but tagged with the alias, making them easy to filter and organize.

---

## Step 1: Configure Email Provider (Google Workspace / Microsoft 365)

### If using Google Workspace:

Your alias is already set up. Emails sent to `biz-search@socalbusinessgroup.com` will arrive in `vance@socalbusinessgroup.com` inbox.

**Create Gmail Filter (Recommended):**

1. Go to Gmail Settings → Filters and Blocked Addresses
2. Create new filter:
   ```
   To: biz-search@socalbusinessgroup.com
   ```
3. Apply label: "M&A Alerts" (create new label)
4. Optional: Skip inbox (if you want them only in the label)
5. Create filter

Now all M&A alerts will be neatly organized!

### If using Microsoft 365:

Same concept - the alias delivers to your main inbox. Set up an Outlook rule:

1. File → Manage Rules & Alerts
2. New Rule → "Apply rule on messages I receive"
3. Condition: "with biz-search@socalbusinessgroup.com in the recipient's address"
4. Action: Move to folder "M&A Alerts" (create if needed)
5. Save

---

## Step 2: Generate App Password

### For Google Workspace:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to https://myaccount.google.com/apppasswords
4. Select:
   - App: "Mail"
   - Device: "Other" → Name it "M&A Deal Finder"
5. Click "Generate"
6. **Save this 16-character password** - you'll need it for the script
   - It will look like: `abcd efgh ijkl mnop`

### For Microsoft 365:

If your organization uses Modern Authentication:
1. You may need admin to create an app password
2. Or use OAuth authentication (more complex setup)
3. Contact IT if app passwords aren't available

**Recommendation:** If Microsoft 365 is complex, run the script locally where you're already authenticated.

---

## Step 3: Set Environment Variables

On your computer:

### Mac/Linux:

```bash
# Add to your ~/.zshrc or ~/.bashrc
export ALERT_EMAIL_ADDRESS='vance@socalbusinessgroup.com'
export ALERT_EMAIL_PASSWORD='abcd efgh ijkl mnop'  # Your app password
export GOOGLE_SHEET_NAME='M&A Opportunities - SoCal Business Group'
export SHEET_SHARE_EMAIL='vance@socalbusinessgroup.com'  # Can share with team too
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Windows PowerShell:

```powershell
setx ALERT_EMAIL_ADDRESS "vance@socalbusinessgroup.com"
setx ALERT_EMAIL_PASSWORD "your-app-password-here"
setx GOOGLE_SHEET_NAME "M&A Opportunities - SoCal Business Group"
```

---

## Step 4: Set Up Email Alerts on M&A Platforms

**IMPORTANT:** When registering on platforms, use the **ALIAS** email:

```
Email: biz-search@socalbusinessgroup.com
```

**Why?**
- All alerts go to your main inbox (vance@socalbusinessgroup.com)
- But they're sent to the alias, so your filter catches them
- Keeps M&A alerts separate from other business emails
- Easy to search: just search for "to:biz-search@socalbusinessgroup.com"

### Priority Platforms (Start Here):

**1. BizBuySell** - https://www.bizbuysell.com/
```
1. Register with: biz-search@socalbusinessgroup.com
2. Account → Saved Searches & Alerts
3. Create Search Alert:
   - States: CA, AZ, NV, NM, TX
   - Revenue: $1M - $10M
   - Cash Flow: $250K+
   - Exclude: Restaurants, Franchises, Food Service
4. Frequency: Weekly (Mondays)
5. Save
```

**2. BizQuest** - https://www.bizquest.com/
```
1. Register: biz-search@socalbusinessgroup.com
2. Email Alerts section
3. Configure same criteria
4. Weekly frequency
```

**3. Business Broker Network** - https://www.businessbroker.net/
**4. BizBen** - https://www.bizben.com/
**5. Strategic Business Brokers** - https://www.businessbrokerphoenixaz.com/
**6. DealStream** - https://dealstream.com/

For complete list of all 28 platforms, see `EMAIL_ALERT_SETUP_GUIDE.md`

---

## Step 5: Update Parser Configuration

The email parser needs to know about your alias. Create a config file:

```bash
cd socal-deal-finder
cat > .env << 'EOF'
# Email Configuration
ALERT_EMAIL_ADDRESS=vance@socalbusinessgroup.com
ALERT_EMAIL_PASSWORD=your-app-password-here
ALERT_EMAIL_ALIAS=biz-search@socalbusinessgroup.com

# Google Sheets Configuration
GOOGLE_SHEET_NAME=M&A Opportunities - SoCal Business Group
SHEET_SHARE_EMAIL=vance@socalbusinessgroup.com

# Optional: Share with team
# SHEET_SHARE_EMAIL=vance@socalbusinessgroup.com,partner@socalbusinessgroup.com
EOF
```

---

## Step 6: Modify Email Parser for Alias

Update the parser to search for emails sent to your alias:

```python
# Quick modification to email_parser.py
# The parser will search for emails where TO address contains the alias

# Instead of just searching FROM addresses, also search TO field
# This ensures we only get emails sent to biz-search@socalbusinessgroup.com
```

I'll create a modified version for you...

---

## Step 7: Test Your Setup

```bash
cd socal-deal-finder

# Test email connection
python test_email_connection.py

# Should show:
# ✅ Connected to vance@socalbusinessgroup.com
# ✅ Authenticated successfully
# ✅ Inbox accessed
# ✓ Found X emails in last 7 days
```

---

## Step 8: Gmail Search Tips

### Manual Searching (Before Parser Runs):

In Gmail, search:
```
to:biz-search@socalbusinessgroup.com
```

This shows ONLY M&A alerts.

Combine with other filters:
```
to:biz-search@socalbusinessgroup.com after:2025/11/01
to:biz-search@socalbusinessgroup.com subject:alert
to:biz-search@socalbusinessgroup.com from:bizbuysell.com
```

### Create Saved Search:

1. Search: `to:biz-search@socalbusinessgroup.com`
2. Click dropdown arrow in search box
3. "Create filter"
4. Choose actions:
   - Apply label: "M&A Alerts"
   - Star it
   - Mark as important
5. Also apply to existing conversations
6. Create filter

Now you have a dedicated section for M&A alerts!

---

## Step 9: Weekly Workflow

**Every Monday Morning:**

### Option 1: Automated (Recommended)
```bash
cd socal-deal-finder
./run_weekly_parser.sh
```

This script will:
1. Parse emails from past 7 days sent to biz-search@socalbusinessgroup.com
2. Apply filters
3. Upload to Google Sheets
4. Show summary

### Option 2: Manual
```bash
cd socal-deal-finder
python email_parser.py
python sheets_uploader.py
```

Then open your Google Sheet to review opportunities.

---

## Advantages of Your Alias Setup

**vs. Separate Gmail Account:**

✅ **One Inbox** - Everything in one place
✅ **Existing Workflow** - No switching between accounts
✅ **Professional Email** - Use your business domain
✅ **Easy Filtering** - Gmail filters keep it organized
✅ **Team Sharing** - Easy to forward or share from business email
✅ **No Extra Logins** - Already authenticated
✅ **Mobile Access** - Your phone already has this email
✅ **Backup** - Same backup as your business email

**How It Works:**
- M&A platforms send to: biz-search@socalbusinessgroup.com
- Emails arrive in: vance@socalbusinessgroup.com inbox
- Gmail filter automatically labels them
- Parser searches for emails TO the alias
- You review in one clean interface

---

## Google Sheets Sharing (For Your Team)

When setting up Google Sheets integration:

```python
# The sheet will be automatically shared with:
SHEET_SHARE_EMAIL=vance@socalbusinessgroup.com

# To share with multiple team members:
# Edit in .env file:
SHEET_SHARE_EMAIL=vance@socalbusinessgroup.com,partner@socalbusinessgroup.com,analyst@socalbusinessgroup.com
```

Team members can then:
- View opportunities
- Update statuses
- Add notes
- See what others are reviewing
- Collaborate on deal evaluation

---

## Security Best Practices

**App Password:**
- Store securely (password manager recommended)
- Don't commit to git (already in .gitignore)
- Rotate every 6-12 months
- Delete if compromised

**Email Alias:**
- Only use for M&A platform registrations
- Don't publish publicly
- If spam increases, can disable alias and create new one
- Alias is free to change anytime

**Google Sheets:**
- Share only with team members who need access
- Use "Editor" permission only for people who should update
- Use "Viewer" for read-only access
- Can revoke access anytime

---

## Troubleshooting

### "No emails found"

Check:
```bash
# In Gmail, search manually:
to:biz-search@socalbusinessgroup.com

# If you see emails, parser just needs alias configuration
# If no emails, alerts aren't set up yet or not sending to alias
```

### "Authentication failed"

- Verify you're using App Password, not regular password
- Check 2-step verification is enabled
- Try generating new App Password
- Verify ALERT_EMAIL_ADDRESS is correct

### "Wrong emails being parsed"

- Parser may be getting all emails instead of just alias
- Verify alias filtering in email_parser.py
- Check Gmail filter is set up correctly

---

## Quick Setup Checklist

- [x] Email alias already created: biz-search@socalbusinessgroup.com
- [ ] Generate App Password for vance@socalbusinessgroup.com
- [ ] Set environment variables (.env file)
- [ ] Create Gmail filter for alias
- [ ] Register on 6 priority M&A platforms using alias email
- [ ] Configure search alerts (same criteria on each)
- [ ] Wait 1-7 days for first emails
- [ ] Test: `python test_email_connection.py`
- [ ] Run parser: `python email_parser.py`
- [ ] Upload to Sheets: `python sheets_uploader.py`
- [ ] Review first curated list!
- [ ] Set up remaining 22 platforms
- [ ] Automate weekly runs

---

## Expected Timeline

**Today (1 hour):**
- Generate App Password
- Set up environment variables
- Test connection
- Register on 6 priority platforms

**This Week (2-3 hours):**
- Register on remaining 22 platforms
- Configure all alerts

**Next Week (Day 7-10):**
- First emails arrive
- Run parser
- See your first curated list!

**Ongoing (30 min/week):**
- Weekly parse & review
- Update statuses
- Track opportunities

---

**You're all set!** With your professional email setup, this will integrate seamlessly into your existing workflow.

Want me to create the modified email parser that specifically filters for your alias?
