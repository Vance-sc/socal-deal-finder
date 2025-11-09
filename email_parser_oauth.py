#!/usr/bin/env python3
"""
Email Alert Parser with Google OAuth Authentication
For SoCal Business Group (vance@socalbusinessgroup.com)
"""

import os
import pickle
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
import config


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailParserOAuth:
    """Parse M&A listing alerts using Google OAuth"""

    def __init__(self, email_address: str, alias_address: str = None, credentials_path: str = 'credentials.json'):
        """
        Initialize email parser with OAuth

        Args:
            email_address: Email address (e.g., vance@socalbusinessgroup.com)
            alias_address: Alias for alerts (e.g., biz-search@socalbusinessgroup.com)
            credentials_path: Path to OAuth credentials JSON from Google Cloud Console
        """
        self.email_address = email_address
        self.alias_address = alias_address or email_address
        self.credentials_path = credentials_path
        self.creds = None
        self.listings = []

        # Platform sender patterns
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
        }

    def authenticate(self) -> bool:
        """Authenticate with Google OAuth"""
        token_path = 'token.pickle'

        # Load existing token if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing OAuth token...")
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ OAuth credentials not found: {self.credentials_path}")
                    print("\nTo set up OAuth:")
                    print("  1. Go to: https://console.cloud.google.com/apis/credentials")
                    print("  2. Create OAuth 2.0 Client ID (Desktop app)")
                    print("  3. Download JSON")
                    print(f"  4. Save as: {self.credentials_path}")
                    print("\nSee OAUTH_SETUP_GUIDE.md for detailed instructions")
                    return False

                print("\n🔐 Google OAuth Login Required")
                print("A browser window will open for you to authenticate...")
                print(f"Please sign in with: {self.email_address}\n")

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        print(f"✓ Authenticated as: {self.email_address}")
        if self.alias_address != self.email_address:
            print(f"✓ Filtering for alias: {self.alias_address}")

        return True

    def fetch_alerts(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch M&A listing alerts using Gmail API

        Args:
            days_back: How many days back to search

        Returns:
            List of parsed listings
        """
        if not self.creds:
            print("❌ Not authenticated")
            return []

        from googleapiclient.discovery import build

        print(f"\n{'='*70}")
        print(f"Searching for M&A alerts from the past {days_back} days...")
        print(f"Filtering for emails TO: {self.alias_address}")
        print(f"{'='*70}\n")

        try:
            # Build Gmail API service
            service = build('gmail', 'v1', credentials=self.creds)

            # Calculate date for query
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

            # Gmail search query
            query = f'to:{self.alias_address} after:{after_date}'

            print(f"Search query: {query}\n")

            # Get messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=500
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                print(f"⚠️  No emails found sent to {self.alias_address}")
                print(f"\nTo verify:")
                print(f"  1. In Gmail, search: to:{self.alias_address}")
                print(f"  2. Check if M&A platform emails appear")
                print(f"  3. If no emails, set up alerts using alias address")
                return []

            print(f"Found {len(messages)} emails sent to alias")

            # Track platforms
            senders_found = {}
            all_listings = []

            # Process each message
            for i, message in enumerate(messages, 1):
                msg_id = message['id']

                # Get full message
                msg = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                # Extract headers
                headers = msg['payload']['headers']
                from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
                date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

                # Identify platform
                platform_name = self._identify_platform(from_addr)
                senders_found[platform_name] = senders_found.get(platform_name, 0) + 1

                # Get email body
                html_content = self._get_message_body(msg)

                if html_content:
                    # Parse listings
                    listings = self._extract_listings_from_html(html_content, platform_name)

                    # Add metadata
                    for listing in listings:
                        listing['email_subject'] = subject
                        listing['email_date'] = date_str
                        listing['source_website'] = platform_name

                    all_listings.extend(listings)

                # Progress indicator
                if i % 10 == 0:
                    print(f"  Processed {i}/{len(messages)} emails...")

            # Show summary
            print(f"\n  M&A Platforms found:")
            for platform, count in sorted(senders_found.items()):
                print(f"    • {platform}: {count} email(s)")

            self.listings = all_listings
            return all_listings

        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _get_message_body(self, message: dict) -> Optional[str]:
        """Extract HTML body from Gmail API message"""
        try:
            if 'parts' in message['payload']:
                # Multipart message
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif 'parts' in part:
                        # Nested parts
                        for subpart in part['parts']:
                            if subpart['mimeType'] == 'text/html' and 'data' in subpart['body']:
                                return base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
            else:
                # Single part message
                if 'data' in message['payload']['body']:
                    return base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        except Exception as e:
            print(f"  Warning: Could not extract email body: {e}")

        return None

    def _identify_platform(self, from_addr: str) -> str:
        """Identify M&A platform from sender address"""
        from_lower = from_addr.lower()

        for platform_name, patterns in self.platform_senders.items():
            for pattern in patterns:
                if pattern in from_lower:
                    return platform_name

        # Extract domain if not recognized
        if '@' in from_addr:
            domain = from_addr.split('@')[-1].split('>')[0]
            return domain.split('.')[0]

        return 'unknown'

    def _extract_listings_from_html(self, html: str, platform: str) -> List[Dict]:
        """Extract business listings from email HTML"""
        soup = BeautifulSoup(html, 'lxml')
        listings = []

        # Find all links
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']

            # Check if looks like listing URL
            if self._is_listing_url(href, platform):
                listing = self._parse_listing_link(link, href, platform, soup)
                if listing:
                    listings.append(listing)

        return listings

    def _is_listing_url(self, url: str, platform: str) -> bool:
        """Check if URL looks like a business listing"""
        listing_patterns = [
            '/business/', '/listing/', '/opportunity/', '/buy/',
            '/for-sale/', '/businesses/', 'business-id', 'listing-id',
        ]

        url_lower = url.lower()
        has_pattern = any(pattern in url_lower for pattern in listing_patterns)

        excluded = ['unsubscribe', 'settings', 'preferences', 'manage', 'email']
        is_excluded = any(pattern in url_lower for pattern in excluded)

        return has_pattern and not is_excluded

    def _parse_listing_link(self, link_element, url: str, platform: str, soup) -> Optional[Dict]:
        """Parse listing details from link and context"""
        listing = {
            'listing_url': url,
            'source_website': platform,
            'date_scraped': datetime.now().isoformat()
        }

        # Extract business name from link text
        link_text = link_element.get_text(strip=True)
        if link_text and 5 < len(link_text) < 200:
            listing['business_name'] = link_text

        # Find parent container
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

            # Extract industry
            industry_keywords = ['Industry:', 'Category:', 'Type:', 'Business Type:']
            for keyword in industry_keywords:
                if keyword in text_content:
                    parts = text_content.split(keyword, 1)
                    if len(parts) > 1:
                        industry_text = parts[1][:50].split('\n')[0].strip()
                        listing['industry'] = industry_text

        # Only return if has minimum data
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
        """Save listings to JSON"""
        os.makedirs('data', exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/email_listings_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(listings, f, indent=2)

        print(f"\n✓ Saved {len(listings)} listings to {filename}")
        return filename

    def print_summary(self, listings: List[Dict]):
        """Print summary of listings"""
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

            if len(by_platform[platform]) > 3:
                print(f"  ... and {len(by_platform[platform]) - 3} more")


def main():
    """Main entry point"""
    print("="*70)
    print("M&A EMAIL ALERT PARSER (GOOGLE OAUTH)")
    print("="*70)
    print("\nUsing Google OAuth for secure authentication\n")

    # Get configuration
    email_address = os.getenv('ALERT_EMAIL_ADDRESS', 'vance@socalbusinessgroup.com')
    alias_address = os.getenv('ALERT_EMAIL_ALIAS', 'biz-search@socalbusinessgroup.com')
    credentials_path = os.getenv('GOOGLE_OAUTH_CREDENTIALS', 'oauth_credentials.json')

    print(f"Configuration:")
    print(f"  Main email: {email_address}")
    print(f"  Alias email: {alias_address}")
    print(f"  OAuth credentials: {credentials_path}")
    print()

    # Initialize parser
    parser = EmailParserOAuth(email_address, alias_address, credentials_path)

    # Authenticate
    if not parser.authenticate():
        return

    try:
        # Fetch alerts
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
            print("  1. Review JSON file in data/ directory")
            print("  2. Upload to Google Sheets: python sheets_uploader.py")
            print("  3. Set up weekly automation")
            print(f"{'='*70}\n")

        else:
            print(f"\n⚠️  No M&A listing alerts found")
            print(f"\nNext steps:")
            print(f"  1. Set up email alerts on M&A platforms")
            print(f"  2. Use alias: {alias_address}")
            print(f"  3. Wait for emails to arrive")
            print(f"  4. Run this script again")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
