# Cloud Shell OAuth Fix - Quick Guide

## Problem
Getting "Access blocked" or "still blocked" when running `python email_parser_oauth.py` in Google Cloud Shell.

## Root Cause
Cloud Shell requires explicit redirect URIs to be configured in the OAuth client. The out-of-band (OOB) flow doesn't work without this configuration.

---

## 5-Minute Fix

### Step 1: Add Redirect URIs to OAuth Client

1. **Open:** https://console.cloud.google.com/apis/credentials
2. **Find:** Your OAuth client named "M&A Deal Finder Desktop"
3. **Click** on it to edit
4. **Under "Authorized redirect URIs"**, click "ADD URI"
5. **Add these two URIs:**
   ```
   http://localhost
   urn:ietf:wg:oauth:2.0:oob
   ```
6. **Click "SAVE"**
7. **Wait 1-2 minutes** for changes to propagate

### Step 2: Test Authentication

```bash
cd ~/socal-deal-finder
python email_parser_oauth.py
```

**Expected flow:**
1. Script prints authorization URL
2. Copy the URL and open in your browser
3. Sign in with: `vance@socalbusinessgroup.com`
4. Click "Allow" to grant Gmail read access
5. Google shows an authorization code
6. Copy the code and paste it into Cloud Shell
7. Script creates `token.pickle` file
8. ✅ Authentication successful!

---

## Why This Happens

| Environment | Redirect URI | Auto-configured? |
|------------|--------------|------------------|
| Local computer | `http://localhost` | ✅ Yes |
| Cloud Shell | `urn:ietf:wg:oauth:2.0:oob` | ❌ No - must add manually |

**Desktop app** OAuth clients in Google Cloud Console do NOT automatically include OOB redirect URIs. You must add them manually when using Cloud Shell or other CLI environments.

---

## Verification

After adding redirect URIs, you should see them listed in the OAuth client configuration:

```
Authorized redirect URIs
  http://localhost
  urn:ietf:wg:oauth:2.0:oob
```

If you see this, you're all set! Run the parser again.

---

## Still Not Working?

### Error: "redirect_uri_mismatch"
- Double-check you added BOTH URIs
- Wait 2-3 minutes for propagation
- Make sure you're editing the right OAuth client

### Error: "invalid_client"
- Re-download `oauth_credentials.json` from Google Cloud Console
- Upload it to Cloud Shell again
- Make sure `.env` points to the right file

### Error: "Access denied"
- Make sure you're signing in with: `vance@socalbusinessgroup.com`
- Check OAuth consent screen has correct scopes (`gmail.readonly`)
- Add yourself as a test user if using "External" user type

---

## Quick Links

- **OAuth Credentials:** https://console.cloud.google.com/apis/credentials
- **Full Setup Guide:** See `OAUTH_SETUP_GUIDE.md`
- **Revoke Access:** https://myaccount.google.com/permissions

---

**Bottom Line:** Add the two redirect URIs to your OAuth client in Google Cloud Console, wait 2 minutes, and try again. This fixes 99% of Cloud Shell OAuth issues.
