"""
Configuration settings for the SoCal M&A Deal Finder
"""

import os
from typing import List, Dict

# Google Cloud Project Settings
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'socal-deal-finder')
GCP_PROJECT_NUMBER = '582967160277'

# Acquisition Criteria
ACQUISITION_CRITERIA = {
    'revenue_min': 1_000_000,      # $1M
    'revenue_max': 10_000_000,     # $10M
    'ebitda_min': 250_000,         # $250K
    'target_states': ['CA', 'AZ', 'NV', 'NM', 'TX'],
    'business_types': [
        'service-based',
        'recurring revenue',
        'repeat customers',
        'essential services'
    ],
    'excluded_types': [
        'restaurant',
        'franchise',
        'bar',
        'food service',
        'digital-only',
        'manufacturing',
        'e-commerce only'
    ]
}

# Target Websites (Priority Order)
PRIORITY_SOURCES: Dict[str, Dict] = {
    'bizbuysell': {
        'name': 'BizBuySell',
        'url': 'https://www.bizbuysell.com/',
        'search_url': 'https://www.bizbuysell.com/businesses-for-sale/',
        'enabled': True,
        'priority': 1
    },
    'bizquest': {
        'name': 'BizQuest',
        'url': 'https://www.bizquest.com/',
        'search_url': 'https://www.bizquest.com/businesses-for-sale/',
        'enabled': True,
        'priority': 2
    },
    'businessbroker': {
        'name': 'Business Broker Network',
        'url': 'https://www.businessbroker.net/',
        'search_url': 'https://www.businessbroker.net/businesses-for-sale/',
        'enabled': True,
        'priority': 3
    },
    'bizben': {
        'name': 'BizBen (CA Specialist)',
        'url': 'https://www.bizben.com/',
        'search_url': 'https://www.bizben.com/businesses-for-sale',
        'enabled': True,
        'priority': 4
    },
    'strategicbb': {
        'name': 'Strategic Business Brokers (Phoenix)',
        'url': 'https://www.businessbrokerphoenixaz.com/',
        'search_url': 'https://www.businessbrokerphoenixaz.com/businesses-for-sale',
        'enabled': True,
        'priority': 5
    },
    'dealstream': {
        'name': 'DealStream',
        'url': 'https://dealstream.com/',
        'search_url': 'https://dealstream.com/businesses-for-sale/',
        'enabled': True,
        'priority': 6
    }
}

# Scraping Settings
REQUEST_TIMEOUT = 15
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
RATE_LIMIT_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# Output Settings
OUTPUT_DIR = 'data'
GOOGLE_SHEET_NAME = 'SoCal M&A Deal Tracker'

# Email Settings
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@socal-deal-finder.com')
EMAIL_TO: List[str] = os.getenv('EMAIL_TO', '').split(',')
SEND_EMAIL_ON_NEW_DEALS = True

# Schedule Settings (for Cloud Scheduler)
SCHEDULE_CRON = '0 8 * * 1'  # Every Monday at 8am
SCHEDULE_TIMEZONE = 'America/Los_Angeles'

# Fields to capture for each listing
LISTING_FIELDS = [
    'listing_id',
    'business_name',
    'city',
    'state',
    'asking_price',
    'revenue',
    'cash_flow',
    'ebitda',
    'industry',
    'business_type',
    'description',
    'listing_url',
    'date_scraped',
    'source_website',
    'year_established',
    'employees',
    'reason_for_sale'
]
