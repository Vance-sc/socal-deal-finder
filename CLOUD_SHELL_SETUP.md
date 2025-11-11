# Cloud Shell Setup Guide - SoCal Deal Finder

## Why Cloud Shell + Secret Manager?

✅ **Secure** - API keys stored in Google Secret Manager, not in files
✅ **Simple** - No OAuth complexity, just one setup script
✅ **Production-Ready** - Same setup works locally and on Cloud Run
✅ **Best Practice** - Follow Google Cloud security recommendations

---

## Quick Start (5 minutes)

### Step 1: Get Your Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Click "API Keys" → "Create Key"
4. Copy your API key (starts with `sk-ant-`)

**💰 Cost**: First $5 is free credit, then pay-as-you-go (~$3/month for weekly searches)

---

### Step 2: Clone Repository (if not already done)

```bash
cd ~
git clone https://github.com/Vance-sc/socal-deal-finder.git
cd socal-deal-finder
git checkout claude/init-socal-deal-finder-011CUxVnhguZfsVvCR5wm8qV
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude API client
- `google-cloud-secret-manager` - Secret Manager client
- `pyyaml` - Config file parsing
- Other utilities

---

### Step 4: Set Up Secret Manager (Automated)

Run our setup script:

```bash
bash scripts/setup-secret-manager.sh
```

**What this script does:**

1. ✅ Enables Secret Manager API in your project
2. ✅ Prompts you for your Anthropic API key
3. ✅ Validates the key format (must start with `sk-ant-`)
4. ✅ Stores it securely in Google Secret Manager
5. ✅ Grants Cloud Run service account access
6. ✅ Shows you the secret name and project info

**Expected output:**

```
========================================================================
  Google Secret Manager Setup - SoCal Deal Finder
========================================================================

✓ Running in Google Cloud Shell
Project ID: socal-deal-finder

[Step 1/4] Enabling Secret Manager API...
✓ Secret Manager API enabled

[Step 2/4] Anthropic API Key

Your API key should start with: sk-ant-

Enter your Anthropic API key: [hidden input]
✓ API key format valid

[Step 3/4] Creating secret in Secret Manager...
Creating new secret...
✓ Secret created

[Step 4/4] Setting up permissions...
Granting access to service account: 582967160277-compute@developer.gserviceaccount.com
✓ Permissions configured

========================================================================
✓ Setup Complete!
========================================================================

Secret Information:
  Name: anthropic-api-key
  Project: socal-deal-finder
  Full Name: projects/582967160277/secrets/anthropic-api-key/versions/latest

Your Anthropic API key is now securely stored in Google Secret Manager.
```

---

### Step 5: Create .env File (Optional)

For local development, you can also use a `.env` file:

```bash
cp .env.example .env
nano .env
```

Add these minimal settings:

```bash
# Google Cloud Project (auto-detected in Cloud Shell)
GOOGLE_PROJECT_ID=socal-deal-finder
GOOGLE_PROJECT_NUMBER=582967160277

# Google Sheets (we'll set this up later)
GOOGLE_SHEET_ID=your-sheet-id-here
GOOGLE_SHEET_NAME=M&A Opportunities

# Email Notifications
NOTIFICATION_EMAIL=vance@socalbusinessgroup.com

# Optional: Override defaults
LOG_LEVEL=INFO
MIN_CONFIDENCE_SCORE=0.65
```

**Note**: You don't need to add `ANTHROPIC_API_KEY` in `.env` - it will automatically come from Secret Manager!

---

### Step 6: Test Configuration

```bash
cd src
python utils.py
```

**Expected output:**

```
====================================================================
  SoCal Business Group - AI-Powered M&A Deal Finder
====================================================================

Loading configuration...
Configuration loaded successfully
Enabled sites: 6
  - BizBuySell (bizbuysell.com)
  - BizQuest (bizquest.com)
  - Business Broker Network (businessbroker.net)
  - BizBen (bizben.com)
  - Strategic Business Brokers Group (businessbrokerphoenixaz.com)
  - DealStream (dealstream.com)
```

If you see this, **configuration is working!** 🎉

---

### Step 7: Test Search Agent

```bash
cd src
python search_agent.py
```

This will:
1. Load API key from Secret Manager
2. Search BizBuySell.com for matching businesses
3. Filter by your acquisition criteria
4. Display results

**Expected output:**

```
====================================================================
  SoCal Business Group - AI-Powered M&A Deal Finder
====================================================================

Loading configuration...
Testing search with BizBuySell...
Starting search | site=BizBuySell | domain=bizbuysell.com

Search complete | site=BizBuySell | total_found=12 | filtered=8
Found 8 deals from BizBuySell

1. HVAC Service Company
   Location: Orange County, CA
   Price: $2,500,000
   Revenue: $3,200,000
   Cash Flow: $450,000
   Confidence: 85%
   URL: https://www.bizbuysell.com/...

[... more results ...]
```

---

## How Secret Manager Integration Works

### Priority Order:

1. **Google Secret Manager** (if available and secret exists)
   → Used in Cloud Shell and Cloud Run
2. **Environment variable** (from `.env` file)
   → Used for local development
3. **Error** if neither is available

### Code Flow:

```python
# In src/utils.py
def load_config():
    # Try Secret Manager first
    api_key = get_config_value("ANTHROPIC_API_KEY", "anthropic-api-key")

    # get_config_value logic:
    # 1. Check Secret Manager: projects/socal-deal-finder/secrets/anthropic-api-key
    # 2. Fall back to: os.getenv("ANTHROPIC_API_KEY")
    # 3. Return None if neither exists
```

---

## Viewing Your Secrets

### Via Cloud Console:

https://console.cloud.google.com/security/secret-manager?project=socal-deal-finder

### Via Command Line:

```bash
# List all secrets
gcloud secrets list --project=socal-deal-finder

# View secret metadata (not the value)
gcloud secrets describe anthropic-api-key --project=socal-deal-finder

# Access the actual secret value
gcloud secrets versions access latest \
  --secret=anthropic-api-key \
  --project=socal-deal-finder
```

---

## Updating Your API Key

If you need to change your API key later:

```bash
# Create a new version (keeps old versions for rollback)
echo -n "sk-ant-new-key-here" | gcloud secrets versions add anthropic-api-key \
  --data-file=- \
  --project=socal-deal-finder
```

Or just run the setup script again:

```bash
bash scripts/setup-secret-manager.sh
```

---

## Troubleshooting

### Error: "Missing required environment variable: ANTHROPIC_API_KEY"

**Cause**: Secret Manager can't find the secret

**Solution**:

```bash
# Check if secret exists
gcloud secrets describe anthropic-api-key --project=socal-deal-finder

# If not found, run setup script again
bash scripts/setup-secret-manager.sh
```

### Error: "Permission denied accessing secret"

**Cause**: Service account doesn't have permission

**Solution**:

```bash
# Grant permission manually
PROJECT_NUMBER=$(gcloud projects describe socal-deal-finder --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project=socal-deal-finder
```

### Error: "google.cloud.secretmanager not found"

**Cause**: Dependencies not installed

**Solution**:

```bash
pip install -r requirements.txt
```

### Want to use .env file instead?

If you prefer local `.env` file over Secret Manager:

```bash
cp .env.example .env
nano .env

# Add your API key:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

The code will automatically fall back to `.env` if Secret Manager isn't available.

---

## Security Best Practices

### ✅ DO:

- Use Secret Manager for production (Cloud Run)
- Use `.env` file for local development only
- Never commit `.env` to git (already in `.gitignore`)
- Rotate API keys periodically
- Use IAM roles to control access

### ❌ DON'T:

- Don't put API keys in code
- Don't commit secrets to git
- Don't share secret values via email/Slack
- Don't use the same key for dev and production

---

## Cost Breakdown

### Google Secret Manager:

- **Storage**: $0.06 per secret-version per month
- **Access**: $0.03 per 10,000 accesses
- **Total**: ~$0.10/month (negligible)

### Anthropic Claude API:

- **First $5**: Free credit
- **After that**: $3/M input tokens, $15/M output tokens
- **Weekly search**: ~70K tokens total = ~$0.60/week
- **Monthly**: ~$2.50/month

### **Total Cost: ~$3/month** 💰

---

## Next Steps

Once Secret Manager is working:

1. ✅ **Secret Manager configured**
2. ⏭️ **Set up Google Sheets** for results storage
3. ⏭️ **Add email notifications** for weekly digest
4. ⏭️ **Deploy to Cloud Run** for automated weekly searches
5. ⏭️ **Set up Cloud Scheduler** to run every Monday 8am

---

## Quick Links

- **Secret Manager Console**: https://console.cloud.google.com/security/secret-manager?project=socal-deal-finder
- **Anthropic Console**: https://console.anthropic.com/
- **Cloud Run Console**: https://console.cloud.google.com/run?project=socal-deal-finder
- **GitHub Repo**: https://github.com/Vance-sc/socal-deal-finder

---

**Ready to test?** Run `bash scripts/setup-secret-manager.sh` now! 🚀
