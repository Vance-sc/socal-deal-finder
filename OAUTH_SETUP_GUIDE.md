# Google OAuth Setup Guide for SoCal Business Group

## Why OAuth Instead of App Password?

✅ **More Secure** - Token-based, can be revoked anytime
✅ **Easier** - No password to remember or rotate
✅ **Professional** - Better for business accounts
✅ **Automatic Refresh** - Tokens refresh automatically
✅ **Granular Permissions** - Only access what's needed (Gmail read-only)

---

## Step-by-Step OAuth Setup (15 minutes)

### Step 1: Go to Google Cloud Console

1. Open: https://console.cloud.google.com/
2. Sign in with: **vance@socalbusinessgroup.com**

### Step 2: Create Project (or Use Existing)

**Option A: Create New Project**
1. Click project dropdown (top left)
2. Click "NEW PROJECT"
3. Project name: "M&A Deal Finder"
4. Click "CREATE"
5. Wait for project to be created
6. Select the new project from dropdown

**Option B: Use Existing Project**
1. Select your existing Google Cloud project

### Step 3: Enable Gmail API

1. In the search bar, type: "Gmail API"
2. Click "Gmail API"
3. Click "ENABLE"
4. Wait a few seconds for it to enable

### Step 4: Configure OAuth Consent Screen

1. Go to: **APIs & Services** → **OAuth consent screen** (left menu)
2. Select user type:
   - Choose **"Internal"** (if you have Google Workspace)
   - Or **"External"** (if personal account)
3. Click "CREATE"

**Fill in the form:**
- **App name**: M&A Deal Finder
- **User support email**: vance@socalbusinessgroup.com
- **Developer contact**: vance@socalbusinessgroup.com
- Click "SAVE AND CONTINUE"

**Scopes:**
- Click "ADD OR REMOVE SCOPES"
- Filter for: gmail.readonly
- Check: `.../auth/gmail.readonly` (Read email messages)
- Click "UPDATE"
- Click "SAVE AND CONTINUE"

**Test users** (if External):
- Click "ADD USERS"
- Add: vance@socalbusinessgroup.com
- Click "ADD"
- Click "SAVE AND CONTINUE"

Click "BACK TO DASHBOARD"

### Step 5: Create OAuth Client ID

1. Go to: **APIs & Services** → **Credentials** (left menu)
2. Click "CREATE CREDENTIALS" (top)
3. Select "OAuth client ID"

**Configure:**
- **Application type**: Desktop app
- **Name**: M&A Deal Finder Desktop
- Click "CREATE"

### Step 6: Download Credentials

1. A dialog will appear with your Client ID
2. Click "DOWNLOAD JSON"
3. Save the file

### Step 7: Move Credentials to Project

```bash
cd ~/socal-deal-finder

# Rename the downloaded file
mv ~/Downloads/client_secret_*.json ./oauth_credentials.json

# Verify it's there
ls -la oauth_credentials.json
```

### Step 8: Update .env File

```bash
# Edit .env file
nano .env

# Add this line:
GOOGLE_OAUTH_CREDENTIALS=oauth_credentials.json
```

Your complete `.env` should look like:
```bash
ALERT_EMAIL_ADDRESS=vance@socalbusinessgroup.com
ALERT_EMAIL_ALIAS=biz-search@socalbusinessgroup.com
GOOGLE_OAUTH_CREDENTIALS=oauth_credentials.json
GOOGLE_SHEET_NAME=M&A Opportunities - SoCal Business Group
```

---

## Step 9: First Run (Authentication)

```bash
cd socal-deal-finder
python email_parser_oauth.py
```

**What will happen:**

1. Script will detect no token exists
2. Opens browser window automatically
3. Google sign-in page appears
4. **Sign in with: vance@socalbusinessgroup.com**
5. Google will ask: "M&A Deal Finder wants to access your Gmail"
6. Click "Allow"
7. Browser shows "The authentication flow has completed"
8. You can close the browser
9. Script continues and creates `token.pickle`

**After first run:**
- Token is saved in `token.pickle`
- Future runs won't need browser
- Token auto-refreshes when expired

---

## Testing Your Setup

```bash
# First run - will open browser
python email_parser_oauth.py

# Should see:
# 🔐 Google OAuth Login Required
# A browser window will open...
# [Browser opens, you sign in]
# ✓ Authenticated as: vance@socalbusinessgroup.com
# ✓ Filtering for alias: biz-search@socalbusinessgroup.com
```

---

## Files Created

After setup, you'll have:

```
socal-deal-finder/
├── oauth_credentials.json    # OAuth client secret (DON'T commit to git)
├── token.pickle              # Stored auth token (DON'T commit to git)
├── .env                      # Your configuration
└── email_parser_oauth.py     # OAuth-based parser
```

**These are already in .gitignore** - won't be committed to git.

---

## Security Best Practices

### ✅ DO:
- Keep `oauth_credentials.json` private
- Keep `token.pickle` private
- Both are already in `.gitignore`
- You can revoke access anytime in Google Account settings

### ❌ DON'T:
- Don't share `oauth_credentials.json`
- Don't commit to git (already protected)
- Don't email the files

### To Revoke Access:

1. Go to: https://myaccount.google.com/permissions
2. Find "M&A Deal Finder"
3. Click "Remove Access"
4. Delete `token.pickle` from your computer

---

## Troubleshooting

### "Error: redirect_uri_mismatch"

**Solution:**
- Make sure you selected "Desktop app" not "Web app"
- Delete oauth_credentials.json and create new one

### "Access blocked: M&A Deal Finder has not completed verification"

**Solution (if using External):**
- This is just a warning
- Click "Advanced"
- Click "Go to M&A Deal Finder (unsafe)"
- This is your own app, so it's safe

**Better Solution:**
- Use "Internal" user type (if you have Google Workspace)
- Or add yourself as a test user

### "oauth_credentials.json not found"

**Solution:**
```bash
# Check the file exists
ls -la oauth_credentials.json

# If not there, download again from Google Cloud Console
# Go to: APIs & Services → Credentials
# Click download icon next to your OAuth client
```

### "Permission denied" or "Insufficient scope"

**Solution:**
- Delete `token.pickle`
- Run again - will re-authenticate with correct scopes
```bash
rm token.pickle
python email_parser_oauth.py
```

---

## Running Weekly (After Setup)

Once authenticated (first time), future runs are automatic:

```bash
# No browser needed - uses stored token
python email_parser_oauth.py
python sheets_uploader.py

# Or use the wrapper script:
./run_weekly_parser_oauth.sh
```

---

## Comparison: OAuth vs App Password

| Feature | OAuth (Recommended) | App Password |
|---------|-------------------|--------------|
| Security | ✅ Token-based | ⚠️ Password-based |
| Setup | 15 min (one-time) | 5 min |
| Daily use | ✅ Automatic | ✅ Automatic |
| Revocation | ✅ Easy (web UI) | ⚠️ Delete password |
| Permissions | ✅ Read-only Gmail | ⚠️ Full email access |
| Business use | ✅ Professional | ⚠️ Less secure |
| Token refresh | ✅ Automatic | N/A |
| Best for | ✅ Production use | Quick testing |

---

## Next Steps

After OAuth is set up:

1. ✅ OAuth credentials created
2. ✅ First authentication completed
3. ✅ Token stored
4. ⏭️ Set up email alerts on M&A platforms
5. ⏭️ Wait for emails to arrive
6. ⏭️ Run parser weekly
7. ⏭️ Review Google Sheet

---

## Quick Reference

### Files:
- `oauth_credentials.json` - OAuth client secret from Google Cloud
- `token.pickle` - Your authenticated session token
- `.env` - Configuration variables

### Commands:
```bash
# First run (opens browser)
python email_parser_oauth.py

# Subsequent runs (automatic)
python email_parser_oauth.py

# Upload to Sheets
python sheets_uploader.py

# All in one
./run_weekly_parser_oauth.sh
```

### Revoke access:
https://myaccount.google.com/permissions

---

**You're all set!** OAuth is configured and much more secure than app passwords.
