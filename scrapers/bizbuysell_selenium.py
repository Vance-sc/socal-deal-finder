"""
BizBuySell.com scraper module using Selenium
"""

from typing import List, Dict, Optional
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import config


class BizBuySellSeleniumScraper:
    """Selenium-based scraper for BizBuySell.com"""

    def __init__(self):
        self.source_name = 'BizBuySell'
        self.base_url = 'https://www.bizbuysell.com'
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        """Set up Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("  ✓ Selenium Chrome driver initialized")
        except Exception as e:
            print(f"  ⚠ Failed to initialize Chrome driver: {e}")
            print("  Try installing: apt-get install chromium-browser chromium-chromedriver")

    def scrape(self) -> List[Dict]:
        """
        Scrape business listings from BizBuySell

        Returns:
            List of listing dictionaries
        """
        if not self.driver:
            print("  ❌ Driver not initialized")
            return []

        listings = []

        try:
            for state in config.ACQUISITION_CRITERIA['target_states']:
                print(f"  Searching in {state}...")

                # Construct search URL for state
                search_url = f"{self.base_url}/search/?q={state}"

                try:
                    self.driver.get(search_url)
                    time.sleep(3)  # Wait for page to load

                    # Get page source and parse with BeautifulSoup
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')

                    # Try to find listings - multiple possible selectors
                    listing_elements = (
                        soup.find_all('div', class_='business-card') or
                        soup.find_all('div', class_='listing') or
                        soup.find_all('article') or
                        soup.find_all('div', attrs={'data-listing': True})
                    )

                    print(f"    Found {len(listing_elements)} potential listings")

                    # If we found elements, let's examine the first one
                    if listing_elements and len(listing_elements) > 0:
                        print(f"    First element classes: {listing_elements[0].get('class', [])}")

                    for element in listing_elements[:10]:  # Limit to first 10 for testing
                        listing = self.parse_listing(element, soup)
                        if listing:
                            listings.append(listing)

                except Exception as e:
                    print(f"    Error scraping {state}: {e}")

                time.sleep(2)  # Rate limiting

        finally:
            self.cleanup()

        return listings

    def parse_listing(self, element, soup) -> Optional[Dict]:
        """
        Parse a BizBuySell listing element

        Args:
            element: BeautifulSoup element containing listing
            soup: Full page soup for context

        Returns:
            Dictionary with listing data or None
        """
        try:
            listing = {}

            # Extract title/business name
            title_elem = (
                element.find('h2') or
                element.find('h3') or
                element.find('a', class_=re.compile(r'title|heading', re.I))
            )
            if title_elem:
                listing['business_name'] = title_elem.get_text(strip=True)

            # Extract location
            location_elem = element.find(class_=re.compile(r'location|address', re.I))
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                listing['city'], listing['state'] = self._parse_location(location_text)

            # Extract asking price
            price_elem = element.find(class_=re.compile(r'price|asking', re.I))
            if price_elem:
                listing['asking_price'] = price_elem.get_text(strip=True)

            # Extract revenue - look for text patterns
            text_content = element.get_text()
            revenue_match = re.search(r'Revenue[:\s]+(\$[\d,\.]+[MK]?)', text_content, re.I)
            if revenue_match:
                listing['revenue'] = revenue_match.group(1)

            # Extract cash flow
            cf_match = re.search(r'Cash Flow[:\s]+(\$[\d,\.]+[MK]?)', text_content, re.I)
            if cf_match:
                listing['cash_flow'] = cf_match.group(1)

            # Extract industry
            industry_elem = element.find(class_=re.compile(r'industry|category', re.I))
            if industry_elem:
                listing['industry'] = industry_elem.get_text(strip=True)

            # Extract description
            desc_elem = element.find('p') or element.find(class_=re.compile(r'description|summary', re.I))
            if desc_elem:
                listing['description'] = desc_elem.get_text(strip=True)[:500]

            # Extract listing URL
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    href = f"{self.base_url}{href}"
                listing['listing_url'] = href

            # Only return if we have minimum required fields
            if listing.get('business_name') and listing.get('listing_url'):
                listing['source_website'] = self.source_name
                listing['listing_id'] = self._generate_listing_id(listing)
                return listing

        except Exception as e:
            print(f"    Error parsing listing: {e}")

        return None

    def _parse_location(self, location_text: str) -> tuple:
        """Parse location text into city and state"""
        parts = [p.strip() for p in location_text.split(',')]
        if len(parts) >= 2:
            return parts[0], parts[-1]
        elif len(parts) == 1:
            if len(parts[0]) == 2 and parts[0].isupper():
                return '', parts[0]
            else:
                return parts[0], ''
        return '', ''

    def _generate_listing_id(self, listing: Dict) -> str:
        """Generate unique ID for a listing"""
        import hashlib
        unique_str = f"{listing.get('source_website', '')}:{listing.get('listing_url', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def passes_criteria(self, listing: Dict) -> bool:
        """Check if listing meets acquisition criteria"""
        criteria = config.ACQUISITION_CRITERIA

        # Check state
        state = listing.get('state', '').upper()
        if state and state not in criteria['target_states']:
            return False

        # Check revenue
        revenue = self._parse_currency(listing.get('revenue'))
        if revenue and (revenue < criteria['revenue_min'] or revenue > criteria['revenue_max']):
            return False

        # Check cash flow
        cash_flow = self._parse_currency(listing.get('cash_flow'))
        if cash_flow and cash_flow < criteria['ebitda_min']:
            return False

        # Check excluded types
        combined_text = f"{listing.get('business_type', '')} {listing.get('industry', '')} {listing.get('description', '')}".lower()
        for excluded in criteria['excluded_types']:
            if excluded.lower() in combined_text:
                return False

        return True

    def _parse_currency(self, value: Optional[str]) -> Optional[int]:
        """Parse currency string to integer"""
        if not value or value == 'N/A':
            return None

        try:
            cleaned = value.replace('$', '').replace(',', '').strip()

            if 'M' in cleaned.upper():
                return int(float(cleaned.upper().replace('M', '')) * 1_000_000)
            elif 'K' in cleaned.upper():
                return int(float(cleaned.upper().replace('K', '')) * 1_000)
            else:
                return int(float(cleaned))

        except (ValueError, AttributeError):
            return None

    def cleanup(self):
        """Clean up Selenium driver"""
        if self.driver:
            self.driver.quit()
            print("  ✓ Browser closed")
