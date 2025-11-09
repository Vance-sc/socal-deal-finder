"""
BizBuySell.com scraper module
"""

from typing import List, Dict, Optional
import re
from scraper import BaseScraper
import config


class BizBuySellScraper(BaseScraper):
    """Scraper for BizBuySell.com"""

    def __init__(self):
        super().__init__('BizBuySell')
        self.base_url = config.PRIORITY_SOURCES['bizbuysell']['search_url']

    def scrape(self) -> List[Dict]:
        """
        Scrape business listings from BizBuySell

        Returns:
            List of listing dictionaries
        """
        listings = []

        # Build search parameters for target states
        for state in config.ACQUISITION_CRITERIA['target_states']:
            print(f"  Searching in {state}...")

            # BizBuySell search parameters
            params = {
                'q': state,
                'locationType': 'state'
            }

            # Fetch search results (first page for now)
            soup = self.fetch_page(self.base_url, params)
            if not soup:
                continue

            # Find listing elements (need to inspect actual HTML structure)
            # This is a template - will need adjustment based on actual page structure
            listing_elements = soup.find_all('div', class_='listing-item') or \
                             soup.find_all('article', class_='result') or \
                             soup.find_all('div', attrs={'data-listing-id': True})

            print(f"    Found {len(listing_elements)} potential listings")

            for element in listing_elements:
                listing = self.parse_listing(element)
                if listing:
                    normalized = self.normalize_listing(listing)
                    listings.append(normalized)

        return listings

    def parse_listing(self, element) -> Optional[Dict]:
        """
        Parse a BizBuySell listing element

        Args:
            element: BeautifulSoup element containing listing

        Returns:
            Dictionary with listing data or None
        """
        try:
            listing = {}

            # Extract title/business name
            title_elem = element.find('h2') or element.find('h3') or element.find('a', class_='listing-title')
            if title_elem:
                listing['business_name'] = title_elem.get_text(strip=True)

            # Extract location
            location_elem = element.find('span', class_='location') or element.find('div', class_='location')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                listing['city'], listing['state'] = self._parse_location(location_text)

            # Extract asking price
            price_elem = element.find('span', class_='price') or element.find('div', class_='asking-price')
            if price_elem:
                listing['asking_price'] = price_elem.get_text(strip=True)

            # Extract revenue
            revenue_elem = element.find('span', class_='revenue') or element.find(text=re.compile(r'Revenue:'))
            if revenue_elem:
                if hasattr(revenue_elem, 'find_next'):
                    listing['revenue'] = revenue_elem.find_next('span').get_text(strip=True)
                else:
                    # Extract from text
                    revenue_match = re.search(r'Revenue:\s*([\$\d,\.MK]+)', str(revenue_elem))
                    if revenue_match:
                        listing['revenue'] = revenue_match.group(1)

            # Extract cash flow
            cf_elem = element.find('span', class_='cash-flow') or element.find(text=re.compile(r'Cash Flow:'))
            if cf_elem:
                if hasattr(cf_elem, 'find_next'):
                    listing['cash_flow'] = cf_elem.find_next('span').get_text(strip=True)
                else:
                    cf_match = re.search(r'Cash Flow:\s*([\$\d,\.MK]+)', str(cf_elem))
                    if cf_match:
                        listing['cash_flow'] = cf_match.group(1)

            # Extract industry/category
            industry_elem = element.find('span', class_='industry') or element.find('span', class_='category')
            if industry_elem:
                listing['industry'] = industry_elem.get_text(strip=True)

            # Extract description
            desc_elem = element.find('p', class_='description') or element.find('div', class_='description')
            if desc_elem:
                listing['description'] = desc_elem.get_text(strip=True)[:500]  # Limit length

            # Extract listing URL
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    href = f"https://www.bizbuysell.com{href}"
                listing['listing_url'] = href

            # Only return if we have minimum required fields
            if listing.get('business_name') and listing.get('listing_url'):
                listing['source_website'] = self.source_name
                return listing

        except Exception as e:
            print(f"    Error parsing listing: {e}")

        return None

    def _parse_location(self, location_text: str) -> tuple:
        """
        Parse location text into city and state

        Args:
            location_text: Location string (e.g., "Los Angeles, CA")

        Returns:
            Tuple of (city, state)
        """
        parts = [p.strip() for p in location_text.split(',')]
        if len(parts) >= 2:
            return parts[0], parts[-1]
        elif len(parts) == 1:
            # Might be just state or just city
            if len(parts[0]) == 2 and parts[0].isupper():
                return '', parts[0]
            else:
                return parts[0], ''
        return '', ''

    def scrape_detailed_listing(self, url: str) -> Optional[Dict]:
        """
        Scrape detailed information from a listing's detail page

        Args:
            url: URL of the listing detail page

        Returns:
            Dictionary with additional listing details
        """
        soup = self.fetch_page(url)
        if not soup:
            return None

        details = {}

        try:
            # Extract year established
            year_elem = soup.find(text=re.compile(r'Year Established:'))
            if year_elem:
                year_match = re.search(r'(\d{4})', year_elem.find_next().get_text())
                if year_match:
                    details['year_established'] = year_match.group(1)

            # Extract number of employees
            emp_elem = soup.find(text=re.compile(r'Employees:'))
            if emp_elem:
                details['employees'] = emp_elem.find_next().get_text(strip=True)

            # Extract reason for sale
            reason_elem = soup.find(text=re.compile(r'Reason for Selling:'))
            if reason_elem:
                details['reason_for_sale'] = reason_elem.find_next().get_text(strip=True)

        except Exception as e:
            print(f"    Error scraping detailed listing: {e}")

        return details
