#!/usr/bin/env python3
"""
Email Alert Parser for M&A Deal Finder (Alias-Optimized Version)
Specifically designed for email alias setups like biz-search@socalbusinessgroup.com
"""

import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from urllib.parse import urlparse
import config


class EmailAlertParserWithAlias:
    """Parse M&A listing alerts from email with alias support"""

    def __init__(self, email_address: str, password: str, alias_address: str = None, imap_server: str = 'imap.gmail.com'):
        """
        Initialize email parser with alias support

        Args:
            email_address: Main email address to login (e.g., vance@socalbusinessgroup.com)
            password: Email password or app-specific password
            alias_address: Alias email used for alerts (e.g., biz-search@socalbusinessgroup.com)
            imap_server: IMAP server address (default: Gmail)
        """
        self.email_address = email_address
        self.password = password
        self.alias_address = alias_address or email_address
        self.imap_server = imap_server
        self.mail = None
        self.listings = []

        # Known M&A platform sender patterns
        self.platform_senders = {
            'bizbuysell': ['bizbuysell.com', 'bizbuysell'],
            'bizquest': ['bizquest.com', 'bizquest'],
            'businessbroker': ['businessbroker.net', 'businessbroker'],
            'bizben': ['bizben.com', 'bizben'],
            'dealstream': ['dealstream.com', 'dealstream'],
            'sunbelt': ['sunbeltnetwork.com', 'sunbelt'],
            'mergernetwork': ['mergernetwork.com', 'merger'],
            'transworld': ['tworld.com', 'transworld'],
            'murphy': ['murphybusiness.com', 'murphy'],
            'flippa': ['flippa.com', 'flippa'],
            'acquire': ['acquire.com', 'acquire'],
            'microacquire': ['microacquire.com', 'microacquire'],
            'empireflippers': ['empireflippers.com', 'empire'],
            'feinternational': ['feinternational.com', 'feinternational'],
            'quietlight': ['quietlight.com', 'quietlight'],
            'loopnet': ['loopnet.com', 'loopnet'],
            'vrbrokers': ['vrbbusinessbrokers.com', 'vrbrokers'],
            'businessmart': ['businessmart.com', 'businessmart'],
            'bizex': ['bizex.net', 'bizex'],
        }

    def connect(self) -> bool:
        """Connect to email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            self.mail.select('inbox')
            print(f"✓ Connected to {self.email_address}")
            if self.alias_address != self.email_address:
                print(f"✓ Filtering for alias: {self.alias_address}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to email: {e}")
            return False

    def disconnect(self):
        """Disconnect from email server"""
        if self.mail:
            self.mail.close()
            self.mail.logout()
            print("✓ Disconnected from email")

    def fetch_alerts(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch M&A listing alerts from the past N days

        Args:
            days_back: How many days back to search

        Returns:
            List of parsed listings
        """
        if not self.mail:
            print("❌ Not connected to email")
            return []

        print(f"\n{'='*70}")
        print(f"Searching for M&A alerts from the past {days_back} days...")
        print(f"Filtering for emails TO: {self.alias_address}")
        print(f"{'='*70}\n")

        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")

        # Search for emails sent TO the alias address
        all_listings = []

        try:
            # Gmail search that combines TO and FROM criteria
            # This ensures we only get M&A platform emails sent to our alias
            print(f"Searching emails sent to {self.alias_address}...")

            # Search for emails to our alias
            search_criteria = f'(TO "{self.alias_address}" SINCE {since_date})'
            _, message_numbers = self.mail.search(None, search_criteria)

            if message_numbers[0]:
                msg_ids = message_numbers[0].split()
                print(f"  Found {len(msg_ids)} emails sent to alias")

                # Group by sender to show summary
                senders_found = {}

                for msg_id in msg_ids:
                    _, msg_data = self.mail.fetch(msg_id, '(RFC822)')
                    email_body = email.message_from_bytes(msg_data[0][1])

                    # Get sender
                    from_addr = email_body['From'].lower()

                    # Identify platform
                    platform_name = self._identify_platform(from_addr)

                    # Track sender
                    senders_found[platform_name] = senders_found.get(platform_name, 0) + 1

                    # Parse listings from this email
                    listings = self._parse_email(msg_id, platform_name)
                    if listings:
                        all_listings.extend(listings)

                # Show summary
                print(f"\n  M&A Platforms found:")
                for platform, count in sorted(senders_found.items()):
                    print(f"    • {platform}: {count} email(s)")

            else:
                print(f"  ⚠️  No emails found sent to {self.alias_address}")
                print(f"\n  Possible reasons:")
                print(f"    1. Haven't set up alerts yet on M&A platforms")
                print(f"    2. Alerts not sending to alias yet (need to wait)")
                print(f"    3. Typo in alias email address")
                print(f"\n  To test: In Gmail, search for: to:{self.alias_address}")

        except Exception as e:
            print(f"  Error searching emails: {e}")

        self.listings = all_listings
        return all_listings

    def _identify_platform(self, from_addr: str) -> str:
        """Identify which M&A platform sent the email"""
        from_lower = from_addr.lower()

        for platform_name, patterns in self.platform_senders.items():
            for pattern in patterns:
                if pattern in from_lower:
                    return platform_name

        # If not recognized, extract domain
        if '@' in from_addr:
            domain = from_addr.split('@')[-1].split('>')[0]
            return domain.split('.')[0]

        return 'unknown'

    def _parse_email(self, msg_id: bytes, platform_name: str) -> List[Dict]:
        """Parse a single email message"""
        try:
            _, msg_data = self.mail.fetch(msg_id, '(RFC822)')
            email_body = email.message_from_bytes(msg_data[0][1])

            # Get subject
            subject = self._decode_subject(email_body['Subject'])

            # Get date
            date_str = email_body['Date']

            # Get email content
            html_content = self._get_email_html(email_body)

            if not html_content:
                return []

            # Parse listings from HTML
            listings = self._extract_listings_from_html(html_content, platform_name)

            # Add email metadata
            for listing in listings:
                listing['email_subject'] = subject
                listing['email_date'] = date_str
                listing['source_website'] = platform_name

            return listings

        except Exception as e:
            print(f"  Error parsing email: {e}")
            return []

    def _decode_subject(self, subject: str) -> str:
        """Decode email subject"""
        if not subject:
            return ''

        decoded_parts = decode_header(subject)
        subject_parts = []

        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                subject_parts.append(content.decode(encoding or 'utf-8', errors='ignore'))
            else:
                subject_parts.append(content)

        return ''.join(subject_parts)

    def _get_email_html(self, email_message) -> Optional[str]:
        """Extract HTML content from email"""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    return payload.decode(charset, errors='ignore')
        else:
            payload = email_message.get_payload(decode=True)
            charset = email_message.get_content_charset() or 'utf-8'
            return payload.decode(charset, errors='ignore')

        return None

    def _extract_listings_from_html(self, html: str, platform: str) -> List[Dict]:
        """Extract business listings from email HTML"""
        soup = BeautifulSoup(html, 'lxml')
        listings = []

        # Common patterns for listing links
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']

            # Check if this looks like a business listing URL
            if self._is_listing_url(href, platform):
                listing = self._parse_listing_link(link, href, platform, soup)
                if listing:
                    listings.append(listing)

        return listings

    def _is_listing_url(self, url: str, platform: str) -> bool:
        """Check if URL looks like a business listing"""
        listing_patterns = [
            '/business/',
            '/listing/',
            '/opportunity/',
            '/buy/',
            '/for-sale/',
            '/businesses/',
            'business-id',
            'listing-id',
        ]

        url_lower = url.lower()
        has_listing_pattern = any(pattern in url_lower for pattern in listing_patterns)

        # Also check if it's not an unsubscribe or settings link
        excluded_patterns = ['unsubscribe', 'settings', 'preferences', 'manage', 'email']
        is_excluded = any(pattern in url_lower for pattern in excluded_patterns)

        return has_listing_pattern and not is_excluded

    def _parse_listing_link(self, link_element, url: str, platform: str, soup) -> Optional[Dict]:
        """Parse details from a listing link and surrounding context"""
        listing = {
            'listing_url': url,
            'source_website': platform,
            'date_scraped': datetime.now().isoformat()
        }

        # Try to extract business name from link text
        link_text = link_element.get_text(strip=True)
        if link_text and len(link_text) > 5 and len(link_text) < 200:
            listing['business_name'] = link_text

        # Try to find parent container with more info
        parent = link_element.find_parent(['div', 'td', 'li', 'article', 'tr'])

        if parent:
            text_content = parent.get_text()

            # Extract price
            price_match = re.search(r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:M|Million|K|Thousand))?', text_content, re.I)
            if price_match:
                listing['asking_price'] = price_match.group(0)

            # Extract revenue
            revenue_match = re.search(r'Revenue[:\s]+\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:M|Million|K))?', text_content, re.I)
            if revenue_match:
                listing['revenue'] = revenue_match.group(0).split(':', 1)[-1].strip()

            # Extract cash flow
            cf_match = re.search(r'(?:Cash Flow|EBITDA|SDE)[:\s]+\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:M|Million|K))?', text_content, re.I)
            if cf_match:
                listing['cash_flow'] = cf_match.group(0).split(':', 1)[-1].strip()

            # Extract location
            location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})', text_content)
            if location_match:
                listing['city'] = location_match.group(1)
                listing['state'] = location_match.group(2)

            # Extract industry/category
            industry_keywords = ['Industry:', 'Category:', 'Type:', 'Business Type:']
            for keyword in industry_keywords:
                if keyword in text_content:
                    parts = text_content.split(keyword, 1)
                    if len(parts) > 1:
                        industry_text = parts[1][:50].split('\n')[0].strip()
                        listing['industry'] = industry_text

        # Only return if we have at least a URL and some data
        if url and (listing.get('business_name') or listing.get('asking_price')):
            return listing

        return None

    def filter_listings(self, listings: List[Dict]) -> List[Dict]:
        """Apply acquisition criteria filters"""
        filtered = []

        for listing in listings:
            # Check state
            state = listing.get('state', '').upper()
            if state and state not in config.ACQUISITION_CRITERIA['target_states']:
                continue

            # Check revenue
            revenue = self._parse_currency(listing.get('revenue'))
            if revenue:
                if revenue < config.ACQUISITION_CRITERIA['revenue_min'] or revenue > config.ACQUISITION_CRITERIA['revenue_max']:
                    continue

            # Check cash flow
            cash_flow = self._parse_currency(listing.get('cash_flow'))
            if cash_flow and cash_flow < config.ACQUISITION_CRITERIA['ebitda_min']:
                continue

            # Check excluded types
            combined_text = f"{listing.get('business_name', '')} {listing.get('industry', '')}".lower()
            excluded = False
            for exclude_type in config.ACQUISITION_CRITERIA['excluded_types']:
                if exclude_type.lower() in combined_text:
                    excluded = True
                    break

            if excluded:
                continue

            filtered.append(listing)

        return filtered

    def _parse_currency(self, value: Optional[str]) -> Optional[int]:
        """Parse currency string to integer"""
        if not value:
            return None

        try:
            cleaned = value.replace('$', '').replace(',', '').strip()

            if 'M' in cleaned.upper() or 'MILLION' in cleaned.upper():
                return int(float(re.sub(r'[^\d.]', '', cleaned)) * 1_000_000)
            elif 'K' in cleaned.upper() or 'THOUSAND' in cleaned.upper():
                return int(float(re.sub(r'[^\d.]', '', cleaned)) * 1_000)
            else:
                return int(float(re.sub(r'[^\d.]', '', cleaned)))

        except (ValueError, AttributeError):
            return None

    def save_to_json(self, listings: List[Dict], filename: str = None):
        """Save listings to JSON file"""
        os.makedirs('data', exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/email_listings_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(listings, f, indent=2)

        print(f"\n✓ Saved {len(listings)} listings to {filename}")
        return filename

    def print_summary(self, listings: List[Dict]):
        """Print summary of found listings"""
        print(f"\n{'='*70}")
        print(f"EMAIL ALERT SUMMARY")
        print(f"{'='*70}\n")

        print(f"Total listings found: {len(listings)}")

        # Group by platform
        by_platform = {}
        for listing in listings:
            platform = listing.get('source_website', 'Unknown')
            by_platform.setdefault(platform, []).append(listing)

        for platform in sorted(by_platform.keys()):
            print(f"\n{platform}: {len(by_platform[platform])} listings")

            for i, listing in enumerate(by_platform[platform][:3], 1):
                print(f"  {i}. {listing.get('business_name', 'N/A')}")
                if listing.get('city') and listing.get('state'):
                    print(f"     Location: {listing.get('city')}, {listing.get('state')}")
                if listing.get('asking_price'):
                    print(f"     Price: {listing.get('asking_price')}")
                if listing.get('revenue'):
                    print(f"     Revenue: {listing.get('revenue')}")

            if len(by_platform[platform]) > 3:
                print(f"  ... and {len(by_platform[platform]) - 3} more")


def main():
    """Main entry point for email parser"""
    print("="*70)
    print("M&A EMAIL ALERT PARSER (ALIAS VERSION)")
    print("="*70)
    print("\nOptimized for email alias setups\n")

    # Get email credentials from environment
    email_address = os.getenv('ALERT_EMAIL_ADDRESS')
    email_password = os.getenv('ALERT_EMAIL_PASSWORD')
    alias_address = os.getenv('ALERT_EMAIL_ALIAS') or email_address

    if not email_address or not email_password:
        print("ERROR: Email credentials not found!")
        print("\nPlease set environment variables:")
        print("  export ALERT_EMAIL_ADDRESS='vance@socalbusinessgroup.com'")
        print("  export ALERT_EMAIL_PASSWORD='your-app-password'")
        print("  export ALERT_EMAIL_ALIAS='biz-search@socalbusinessgroup.com'")
        return

    print(f"Configuration:")
    print(f"  Main email: {email_address}")
    print(f"  Alias email: {alias_address}")
    print()

    # Initialize parser
    parser = EmailAlertParserWithAlias(email_address, email_password, alias_address)

    # Connect
    if not parser.connect():
        return

    try:
        # Fetch alerts from past 7 days
        all_listings = parser.fetch_alerts(days_back=7)

        print(f"\n{'='*70}")
        print(f"Found {len(all_listings)} total listings from email alerts")
        print(f"{'='*70}")

        if all_listings:
            # Apply filters
            print("\nApplying acquisition criteria filters...")
            filtered_listings = parser.filter_listings(all_listings)

            print(f"✓ {len(filtered_listings)} listings meet criteria")

            # Save results
            parser.save_to_json(filtered_listings)

            # Print summary
            parser.print_summary(filtered_listings)

            print(f"\n{'='*70}")
            print("Next steps:")
            print("  1. Review the saved JSON file")
            print("  2. Import to Google Sheets: python sheets_uploader.py")
            print("  3. Set up weekly automation")
            print(f"{'='*70}\n")

        else:
            print("\n⚠ No M&A listing alerts found in the past 7 days")
            print(f"\nTo verify your alias is working:")
            print(f"  1. In Gmail, search: to:{alias_address}")
            print(f"  2. Check if M&A platform emails appear")
            print(f"  3. If no emails, set up alerts using alias address")

    finally:
        parser.disconnect()


if __name__ == '__main__':
    main()
