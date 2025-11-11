# Quick Start Guide - AI-Powered M&A Deal Finder

## Step 1: Get Your Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Click "API Keys" in the left menu
4. Click "Create Key"
5. Copy your API key (starts with `sk-ant-`)

## Step 2: Set Up Environment

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env and add your API key
nano .env

# Add this line (replace with your actual key):
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Also update these if needed:
GOOGLE_SHEET_ID=your-sheet-id  # We'll create this later
NOTIFICATION_EMAIL=vance@socalbusinessgroup.com
```

## Step 3: Test Configuration

```bash
# Test that config loads properly
cd src
python utils.py
```

You should see:
```
====================================================================
  SoCal Business Group - AI-Powered M&A Deal Finder
====================================================================

Configuration loaded successfully
Enabled sites: 6
  - BizBuySell (bizbuysell.com)
  - BizQuest (bizquest.com)
  - Business Broker Network (businessbroker.net)
  - BizBen (bizben.com)
  - Strategic Business Brokers Group (businessbrokerphoenixaz.com)
  - DealStream (dealstream.com)
```

## Step 4: Test Search with ONE Site (BizBuySell)

```bash
# Run search agent test
cd src
python search_agent.py
```

This will:
1. Search BizBuySell.com for businesses matching our criteria
2. Use Claude API with web search
3. Filter results by confidence score (65%+)
4. Display found opportunities

**Expected output:**
```
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

2. Plumbing & Drain Services
   Location: San Diego, CA
   Price: $1,800,000
   Revenue: $2,100,000
   Cash Flow: $380,000
   Confidence: 78%
   URL: https://www.bizbuysell.com/...

[... more results ...]
```

## Step 5: Understanding the Results

Each result includes:
- **Business Name**: May be "Undisclosed" for confidentiality
- **Location**: City and state
- **Asking Price**: Listed price
- **Revenue**: Annual revenue
- **Cash Flow**: EBITDA/SDE (whichever the listing uses)
- **Confidence Score**: AI assessment of how well it matches criteria (0-100%)
- **URL**: Direct link to the listing

## What's Happening Under the Hood?

1. **Search Agent** constructs an intelligent query for BizBuySell
2. **Claude API** uses its web search tool to find matching listings
3. **AI Analysis** extracts structured data and filters by criteria:
   - Revenue: $1M - $10M ✓
   - Cash Flow: $250K+ ✓
   - Location: CA, AZ, NV, NM, TX ✓
   - Type: Service-based with recurring revenue ✓
   - Excludes: Restaurants, franchises, etc. ✓
4. **Confidence Scoring** ranks each match
5. **Results** are returned as structured data

## Cost of This Test

- ~50K input tokens + ~20K output tokens
- Input: 50K × $3/1M = $0.15
- Output: 20K × $15/1M = $0.30
- **Total: ~$0.45 for one site**

Weekly with all 6 sites: ~$3/week = **$12/month**

## Troubleshooting

### Error: "Missing required environment variable: ANTHROPIC_API_KEY"

**Solution**: Make sure you copied `.env.example` to `.env` and added your API key

```bash
cp .env.example .env
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Error: "Invalid ANTHROPIC_API_KEY format"

**Solution**: API key must start with `sk-ant-`

Check your key at: https://console.anthropic.com/settings/keys

### Error: "ModuleNotFoundError: No module named 'anthropic'"

**Solution**: Install dependencies

```bash
pip install -r requirements.txt
```

### No results found

**Possible reasons**:
1. BizBuySell may not have businesses matching ALL criteria right now
2. Try lowering `MIN_CONFIDENCE_SCORE` in `.env`:
   ```bash
   MIN_CONFIDENCE_SCORE=0.50  # Lower threshold
   ```
3. Check that you have internet connectivity
4. Verify API key is valid

## Next Steps

Once the search agent is working with BizBuySell:

1. ✅ **Search ONE site works!**
2. ⏭️ **Add Google Sheets integration** to save results
3. ⏭️ **Test with all 6 priority sites**
4. ⏭️ **Add email notifications**
5. ⏭️ **Deploy to Cloud Run**
6. ⏭️ **Set up weekly scheduler**

---

## Development Tips

### Test with Dev Mode (No API Calls)

```bash
# In .env
DEV_MODE=true
```

This will skip API calls and use mock data for testing.

### Increase Logging

```bash
# In .env
LOG_LEVEL=DEBUG
```

### Adjust Criteria

Edit `config/criteria.yaml` to change:
- Revenue range
- Cash flow minimum
- Target states
- Business types
- Exclusions
- Confidence score threshold

All without touching code!

---

**Ready to test?** Run `python src/search_agent.py` and see the magic! ✨
