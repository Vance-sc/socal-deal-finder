# SoCal M&A Deal Finder

Automated business acquisition deal finder for SoCal Business Group. Monitors 28+ M&A marketplaces weekly and sends filtered results matching specific acquisition criteria.

## 🚀 Recommended Approach: Email Alert System (FREE)

**NEW:** We've built a 100% FREE email-based system that works perfectly!

Instead of web scraping (which faces anti-bot protection), use email alerts from the platforms themselves:

1. **Set up email alerts** on all 28 M&A platforms (2-3 hours one-time setup)
2. **Automated parser** extracts listings from weekly emails
3. **Filtered results** uploaded to Google Sheets automatically
4. **Review curated list** instead of visiting 28 websites

**Benefits:**
- ✅ 100% FREE ($0/month)
- ✅ Legal (uses platforms' own notification features)
- ✅ Covers all 28 platforms
- ✅ No anti-bot issues
- ✅ Saves 10+ hours/week

**Quick Start:** See `QUICK_START.md` or `EMAIL_ALERT_SETUP_GUIDE.md`

---

## Overview

This project automates the discovery of business acquisition opportunities by:
- **Email Alerts** - Parsing weekly alerts from 28 M&A marketplaces (RECOMMENDED)
- **Web Scraping** - Direct scraping where accessible (requires paid services)
- Filtering based on revenue, cash flow, location, and business type criteria
- Storing results in Google Sheets for easy review
- Running automatically on a weekly schedule

## Acquisition Criteria

**Target Profile:**
- Revenue: $1M - $10M annually
- EBITDA/SDE: $250K+ annually
- Location: Southern California and nearby markets (CA, AZ, NV, NM, TX)
- Business Type: Service-based companies with recurring/repeat revenue

**Excluded:**
- Restaurants, bars, food service
- Franchises
- Digital-only businesses
- Manufacturing
- E-commerce only

## Target Websites

**Priority Sites (Phase 1):**
1. BizBuySell - https://www.bizbuysell.com/ ✓
2. BizQuest - https://www.bizquest.com/
3. Business Broker Network - https://www.businessbroker.net/
4. BizBen - https://www.bizben.com/ (California specialist)
5. Strategic Business Brokers - https://www.businessbrokerphoenixaz.com/
6. DealStream - https://dealstream.com/

**Additional Sites (Phase 2):**
Full list of 28 marketplaces in tracking spreadsheet

## Project Structure

```
socal-deal-finder/
├── EMAIL ALERT SYSTEM (RECOMMENDED - FREE)
│   ├── email_parser.py              # Parse M&A email alerts
│   ├── sheets_uploader.py           # Upload to Google Sheets
│   ├── test_email_connection.py     # Test email setup
│   ├── EMAIL_ALERT_SETUP_GUIDE.md   # Complete setup guide
│   └── QUICK_START.md               # Fast setup (1 hour)
│
├── WEB SCRAPING SYSTEM (Alternative - Requires Paid Services)
│   ├── main.py                      # Main scraper entry point
│   ├── scraper.py                   # Base scraper classes
│   ├── scrapers/                    # Website-specific scrapers
│   ├── SCRAPING_SOLUTIONS.md        # Anti-bot solutions
│   └── test_all_sites.py            # Test website accessibility
│
├── SHARED COMPONENTS
│   ├── config.py                    # Configuration settings
│   ├── google_integrations.py       # Google Sheets & Gmail
│   ├── requirements.txt             # Python dependencies
├── Dockerfile                 # Container configuration
├── cloudbuild.yaml           # Cloud Build configuration
├── deploy.sh                 # Deployment script
├── setup_scheduler.sh        # Cloud Scheduler setup
├── scrapers/                 # Individual website scrapers
│   ├── __init__.py
│   └── bizbuysell.py        # BizBuySell scraper
├── data/                     # Output directory (gitignored)
└── .env.example             # Environment variables template
```

## Local Development

### Prerequisites

- Python 3.11+
- Google Cloud SDK (for deployment)
- Google Cloud project with billing enabled

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Vance-sc/socal-deal-finder.git
cd socal-deal-finder
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Set up Google Cloud credentials (see Authentication section)

### Run Locally

```bash
python main.py
```

This will:
- Scrape enabled websites
- Apply acquisition criteria filters
- Save results to `data/deals_[timestamp].json`
- Display summary in console

## Google Cloud Authentication

### For Google Sheets API

1. Create a service account:
```bash
gcloud iam service-accounts create socal-deal-finder \
    --display-name="SoCal Deal Finder Service Account"
```

2. Grant necessary roles:
```bash
gcloud projects add-iam-policy-binding socal-deal-finder \
    --member="serviceAccount:socal-deal-finder@socal-deal-finder.iam.gserviceaccount.com" \
    --role="roles/sheets.editor"
```

3. Create and download key:
```bash
gcloud iam service-accounts keys create credentials.json \
    --iam-account=socal-deal-finder@socal-deal-finder.iam.gserviceaccount.com
```

4. Set environment variable:
```bash
export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
```

### For Gmail API

Similar process as Sheets, but add Gmail send scope.
Alternatively, use SendGrid or similar for production email.

## Deployment to Google Cloud Run

### Initial Setup

1. Set your GCP project:
```bash
gcloud config set project socal-deal-finder
```

2. Enable required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

3. Run deployment script:
```bash
./deploy.sh
```

### Set Up Weekly Schedule

After deploying, set up Cloud Scheduler:

```bash
./setup_scheduler.sh
```

This creates a job that runs every Monday at 8am Pacific Time.

### Manual Trigger

To test the scraper manually:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe socal-deal-finder \
    --region us-west1 --format 'value(status.url)')

# Trigger scraper
curl $SERVICE_URL
```

## Configuration

Edit `config.py` to customize:

- **Acquisition criteria** - Revenue range, cash flow minimum, excluded types
- **Target states** - Which states to search
- **Sources** - Enable/disable specific websites
- **Schedule** - Change scraping frequency
- **Output format** - JSON, CSV, or both

## Adding New Scrapers

To add a new website scraper:

1. Create new file in `scrapers/` directory:
```python
# scrapers/bizquest.py
from scraper import BaseScraper

class BizQuestScraper(BaseScraper):
    def __init__(self):
        super().__init__('BizQuest')

    def scrape(self):
        # Implementation here
        pass

    def parse_listing(self, element):
        # Parse logic here
        pass
```

2. Add to `scrapers/__init__.py`:
```python
from .bizquest import BizQuestScraper
__all__ = ['BizBuySellScraper', 'BizQuestScraper']
```

3. Register in `main.py`:
```python
from scrapers import BizBuySellScraper, BizQuestScraper

finder.add_scraper(BizBuySellScraper())
finder.add_scraper(BizQuestScraper())
```

## Output

### JSON Format

Each listing includes:
```json
{
  "listing_id": "unique-hash",
  "business_name": "Example Service Company",
  "city": "Los Angeles",
  "state": "CA",
  "asking_price": "$2,500,000",
  "revenue": "$3,200,000",
  "cash_flow": "$450,000",
  "industry": "Professional Services",
  "description": "Established business with...",
  "listing_url": "https://...",
  "date_scraped": "2025-11-09T10:30:00",
  "source_website": "BizBuySell"
}
```

### Google Sheets

Results are saved to a Google Sheet named "SoCal M&A Deal Tracker" with:
- Automatic deduplication
- Formatted headers
- All listing fields in columns
- Shareable with team members

## Monitoring & Logs

View Cloud Run logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=socal-deal-finder" \
    --limit 50 --format json
```

View Cloud Scheduler job status:
```bash
gcloud scheduler jobs describe socal-deal-finder-weekly --location us-west1
```

## Cost Estimation

**Google Cloud Run:**
- Free tier: 2 million requests/month
- Expected usage: ~4 requests/month (weekly schedule)
- Cost: $0/month (well within free tier)

**Cloud Scheduler:**
- $0.10 per job per month
- Cost: $0.10/month

**Container Registry:**
- $0.026 per GB/month
- Expected: ~500MB image
- Cost: ~$0.01/month

**Total estimated cost: ~$0.11/month**

## Troubleshooting

### Scraper returns no results

1. Website HTML structure may have changed - inspect and update selectors
2. Check for rate limiting - increase `RATE_LIMIT_DELAY` in config
3. Verify filters aren't too restrictive

### Google Sheets authentication fails

1. Verify service account has Sheets API enabled
2. Check credentials file path is correct
3. Ensure sheet is shared with service account email

### Cloud Run timeout

1. Increase timeout in `deploy.sh` (max 60 minutes for 2nd gen)
2. Consider reducing number of scraped pages per run
3. Add pagination/batching for large datasets

## Security Notes

- Never commit credentials to git (use `.gitignore`)
- Store sensitive data in Secret Manager
- Use service accounts with minimum required permissions
- Rotate credentials regularly

## Future Enhancements

- [ ] Add remaining 22 website scrapers
- [ ] Implement Selenium for JavaScript-heavy sites
- [ ] Add ML-based relevance scoring
- [ ] Create web dashboard for results
- [ ] Add Slack notifications
- [ ] Implement change tracking (price updates, status changes)
- [ ] Add historical trending analysis

## License

Proprietary - SoCal Business Group

## Support

For issues or questions, contact the development team.
