"""
SoCal M&A Deal Finder - Base scraper classes and utilities
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import config


class BaseScraper(ABC):
    """Base class for all business listing scrapers"""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        self.listings = []

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrape listings from the source

        Returns:
            List of listing dictionaries
        """
        pass

    @abstractmethod
    def parse_listing(self, element) -> Optional[Dict]:
        """
        Parse a single listing element

        Args:
            element: BeautifulSoup element or data structure

        Returns:
            Dictionary with listing information or None
        """
        pass

    def fetch_page(self, url: str, params: Optional[Dict] = None) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page

        Args:
            url: URL to fetch
            params: Optional query parameters

        Returns:
            BeautifulSoup object or None on error
        """
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            time.sleep(config.RATE_LIMIT_DELAY)  # Rate limiting
            return BeautifulSoup(response.content, 'lxml')

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def generate_listing_id(self, listing: Dict) -> str:
        """
        Generate a unique ID for a listing

        Args:
            listing: Listing dictionary

        Returns:
            Unique hash ID
        """
        # Create hash from source + URL
        unique_str = f"{listing.get('source_website', '')}:{listing.get('listing_url', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def passes_criteria(self, listing: Dict) -> bool:
        """
        Check if a listing meets acquisition criteria

        Args:
            listing: Listing dictionary

        Returns:
            True if listing meets criteria
        """
        criteria = config.ACQUISITION_CRITERIA

        # Check state
        state = listing.get('state', '').upper()
        if state and state not in criteria['target_states']:
            return False

        # Check revenue
        revenue = self._parse_currency(listing.get('revenue'))
        if revenue and (revenue < criteria['revenue_min'] or revenue > criteria['revenue_max']):
            return False

        # Check cash flow/EBITDA
        cash_flow = self._parse_currency(listing.get('cash_flow') or listing.get('ebitda'))
        if cash_flow and cash_flow < criteria['ebitda_min']:
            return False

        # Check excluded types
        business_type = listing.get('business_type', '').lower()
        industry = listing.get('industry', '').lower()
        description = listing.get('description', '').lower()

        combined_text = f"{business_type} {industry} {description}"

        for excluded in criteria['excluded_types']:
            if excluded.lower() in combined_text:
                return False

        return True

    def _parse_currency(self, value: Optional[str]) -> Optional[int]:
        """
        Parse currency string to integer

        Args:
            value: Currency string (e.g., "$1,500,000", "$1.5M")

        Returns:
            Integer value or None
        """
        if not value or value == 'N/A':
            return None

        try:
            # Remove currency symbols and whitespace
            cleaned = value.replace('$', '').replace(',', '').strip()

            # Handle M (millions) and K (thousands)
            if 'M' in cleaned.upper():
                return int(float(cleaned.upper().replace('M', '')) * 1_000_000)
            elif 'K' in cleaned.upper():
                return int(float(cleaned.upper().replace('K', '')) * 1_000)
            else:
                return int(float(cleaned))

        except (ValueError, AttributeError):
            return None

    def normalize_listing(self, raw_listing: Dict) -> Dict:
        """
        Normalize a listing to standard format

        Args:
            raw_listing: Raw listing data

        Returns:
            Normalized listing dictionary
        """
        listing = {field: raw_listing.get(field, '') for field in config.LISTING_FIELDS}
        listing['listing_id'] = self.generate_listing_id(raw_listing)
        listing['date_scraped'] = datetime.now().isoformat()
        listing['source_website'] = self.source_name
        return listing


class DealFinder:
    """Main orchestrator for finding M&A deals"""

    def __init__(self):
        self.scrapers = []
        self.all_listings = []

    def add_scraper(self, scraper: BaseScraper):
        """Add a scraper to the finder"""
        self.scrapers.append(scraper)

    def run(self) -> List[Dict]:
        """
        Run all scrapers and collect listings

        Returns:
            List of all qualified listings
        """
        print(f"Starting M&A Deal Finder - {datetime.now()}")

        for scraper in self.scrapers:
            print(f"\nScraping {scraper.source_name}...")
            try:
                listings = scraper.scrape()
                qualified = [l for l in listings if scraper.passes_criteria(l)]
                self.all_listings.extend(qualified)
                print(f"  Found {len(listings)} listings, {len(qualified)} meet criteria")
            except Exception as e:
                print(f"  Error scraping {scraper.source_name}: {e}")

        print(f"\n✓ Total qualified listings: {len(self.all_listings)}")
        return self.all_listings

    def get_results(self) -> List[Dict]:
        """Get all collected listings"""
        return self.all_listings
