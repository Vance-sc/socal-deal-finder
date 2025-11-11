# SoCal Deal Finder - AI Search Architecture

## Architecture Change: Email Parsing → AI Web Search

### Previous Approach (Deprecated)
❌ Email alerts from M&A platforms
❌ Wait for platforms to send alerts
❌ Limited to alert frequency
❌ Complex OAuth setup

### New Approach (Current)
✅ **Proactive AI-powered web search**
✅ **Weekly intelligent search of all 28 sites**
✅ **Claude API with built-in web search**
✅ **Smart filtering and assessment**

---

## Why Anthropic Claude API?

| Feature | Claude API | Perplexity | Google CSE |
|---------|-----------|------------|------------|
| Intelligence | ✅ Highest | ⭐ Good | ❌ Basic |
| Filtering | ✅ Natural language | ⭐ Moderate | ❌ Manual |
| Adaptability | ✅ Handles site changes | ⭐ Moderate | ❌ Rigid |
| Cost (monthly) | ✅ $1.80 | ❌ $5-10 | ⭐ $0-5 |
| Citations | ✅ Yes | ✅ Yes | ⭐ Limited |
| Setup | ✅ Simple | ⭐ Moderate | ⭐ Moderate |

**Winner: Claude API** - Best intelligence + lowest cost

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Cloud Scheduler                        │
│              (Every Monday 8am PT)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Cloud Run Instance                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. Load Config (sites.yaml, criteria.yaml)     │  │
│  │  2. For each of 28 sites:                       │  │
│  │     - Construct search query                     │  │
│  │     - Call Claude API with web search tool      │  │
│  │     - Extract & filter deals                     │  │
│  │     - Deduplicate results                        │  │
│  │  3. Write to Google Sheets                       │  │
│  │  4. Send email digest                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  Google Sheets   │    │   Gmail API      │
│   (Results)      │    │ (Notifications)  │
└──────────────────┘    └──────────────────┘
```

---

## How It Works

### 1. Search Strategy (Per Site)

For each of the 28 websites, construct intelligent queries:

```python
# Example for BizBuySell
query = """
Search site:bizbuysell.com for:
- Service-based businesses with recurring revenue
- Located in: California, Arizona, Nevada, New Mexico, or Texas
- Revenue between $1M - $10M
- Cash flow/EBITDA over $250K
- Exclude: restaurants, franchises, bars, food service
- Posted in last 90 days
"""

# Claude API with web search finds and analyzes
response = anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=[{"type": "web_search"}],
    messages=[{"role": "user", "content": query}]
)
```

### 2. Intelligent Filtering

Claude analyzes each listing and extracts:
- Business name
- Location (city, state)
- Asking price
- Revenue (annual)
- Cash flow/EBITDA
- Industry/business type
- Description
- Why it matches criteria
- Match confidence score

### 3. Deduplication

Track by URL and business name to avoid duplicates across:
- Multiple sites listing same business
- Same business re-posted
- Historical results from previous weeks

### 4. Results Storage

Google Sheets with columns:
```
| Date Found | Source | Business | Location | Price | Revenue |
| Cash Flow | Industry | Description | URL | AI Assessment | Score |
```

### 5. Email Digest

Weekly email to: `vance@socalbusinessgroup.com`

```
📊 Weekly M&A Deal Finder Results

🎯 Found 12 new opportunities this week

Top Matches:
1. [Business Name] - $3.2M revenue, $450K EBITDA, Orange County, CA
   Why: Service-based with 90% recurring revenue, strong margins

2. [Business Name] - $5.1M revenue, $800K EBITDA, Phoenix, AZ
   Why: Essential services, local monopoly, operational upside

[View full results in Google Sheets]

Stats:
- BizBuySell: 5 matches
- BizQuest: 3 matches
- BizBen: 2 matches
- DealStream: 2 matches
```

---

## Cost Analysis

### Weekly Run:
- 28 sites × ~2K tokens/site = 56K input tokens
- 28 sites × ~1K tokens/site = 28K output tokens
- Input cost: 56K × $3/1M = $0.17
- Output cost: 28K × $15/1M = $0.42
- **Total per run: $0.59**

### Monthly:
- 4 runs × $0.59 = **$2.36/month**

### Other Costs:
- Google Sheets API: Free (up to 500 requests/100 seconds)
- Gmail API: Free (up to 1 billion requests/day)
- Cloud Run: ~$0.50/month (minimal compute time)
- Cloud Scheduler: $0.10/month (1 job)

**Total Monthly Cost: ~$3/month** 🎉

---

## Project Structure

```
socal-deal-finder/
├── README.md                    # Setup and usage guide
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Cloud Run container
├── .env.example                 # Environment variables template
├── .gitignore                   # Ignore secrets
├── config/
│   ├── sites.yaml              # 28 M&A websites with search patterns
│   └── criteria.yaml           # Acquisition criteria (easy to modify)
├── src/
│   ├── main.py                 # Cloud Run entry point
│   ├── search_agent.py         # Claude API search logic
│   ├── filters.py              # Criteria filtering & scoring
│   ├── sheets_manager.py       # Google Sheets operations
│   ├── notifier.py             # Email digest generator
│   └── utils.py                # Helper functions
├── tests/
│   └── test_search.py          # Unit tests
└── docs/
    ├── SETUP.md                # Step-by-step setup
    └── DEPLOYMENT.md           # Cloud Run deployment
```

---

## Environment Variables

```bash
# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Google Cloud
GOOGLE_PROJECT_ID=socal-deal-finder
GOOGLE_PROJECT_NUMBER=582967160277

# Google Sheets
GOOGLE_SHEET_ID=<your-sheet-id>
GOOGLE_SHEET_NAME=M&A Opportunities

# Email Notifications
NOTIFICATION_EMAIL=vance@socalbusinessgroup.com

# Search Config
MAX_RESULTS_PER_SITE=10
SEARCH_LOOKBACK_DAYS=90
MIN_CONFIDENCE_SCORE=0.7
```

---

## Deployment Steps

1. **Local Development**
   ```bash
   git clone https://github.com/Vance-sc/socal-deal-finder
   cd socal-deal-finder
   pip install -r requirements.txt
   cp .env.example .env
   # Add API keys to .env
   python src/main.py  # Test locally
   ```

2. **Google Cloud Setup**
   ```bash
   # Enable APIs
   gcloud services enable run.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   gcloud services enable sheets.googleapis.com
   gcloud services enable gmail.googleapis.com

   # Create service account
   gcloud iam service-accounts create deal-finder \
     --display-name="M&A Deal Finder"
   ```

3. **Build & Deploy to Cloud Run**
   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/socal-deal-finder/search-agent

   # Deploy to Cloud Run
   gcloud run deploy deal-finder \
     --image gcr.io/socal-deal-finder/search-agent \
     --platform managed \
     --region us-west1 \
     --set-env-vars ANTHROPIC_API_KEY=sk-ant-...
   ```

4. **Configure Cloud Scheduler**
   ```bash
   # Create weekly job (Monday 8am PT)
   gcloud scheduler jobs create http deal-finder-weekly \
     --location us-west1 \
     --schedule "0 8 * * 1" \
     --time-zone "America/Los_Angeles" \
     --uri "<Cloud Run URL>" \
     --http-method POST
   ```

---

## Advantages Over Email Approach

| Feature | Email Parsing | AI Search |
|---------|--------------|-----------|
| Speed | ❌ Wait for alerts | ✅ Instant search |
| Coverage | ❌ Only alerted deals | ✅ All active listings |
| Frequency | ❌ Platform-dependent | ✅ Weekly (configurable) |
| Setup | ❌ Complex OAuth | ✅ Simple API key |
| Intelligence | ❌ Basic parsing | ✅ Smart assessment |
| Cost | ✅ Free | ✅ $3/month |
| Maintenance | ❌ High (email changes) | ✅ Low (AI adapts) |

---

## Next Steps

1. ✅ Choose AI approach (Claude API)
2. ⏭️ Set up project structure
3. ⏭️ Implement search agent
4. ⏭️ Test with 6 priority sites
5. ⏭️ Add all 28 sites
6. ⏭️ Deploy to Cloud Run
7. ⏭️ Configure weekly scheduler
8. ⏭️ Monitor first run

---

**Estimated Development Time: 3-4 hours**
**Estimated Monthly Cost: $3**
**Value: Priceless (find your next acquisition!)** 🎯
