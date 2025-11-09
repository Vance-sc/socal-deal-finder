#!/usr/bin/env python3
"""
Upload parsed email listings to Google Sheets
Creates a curated, filterable spreadsheet of M&A opportunities
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import gspread
from google.oauth2.service_account import Credentials
import config


class SheetsUploader:
    """Upload M&A listings to Google Sheets"""

    def __init__(self, credentials_path: str = None):
        """
        Initialize Sheets uploader

        Args:
            credentials_path: Path to Google service account JSON
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.client = None
        self.sheet = None

        if self.credentials_path and os.path.exists(self.credentials_path):
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )

            self.client = gspread.authorize(credentials)
            print("✓ Authenticated with Google Sheets")

        except Exception as e:
            print(f"⚠ Failed to authenticate: {e}")
            print("\nTo set up Google Sheets:")
            print("  1. Create service account: https://console.cloud.google.com/iam-admin/serviceaccounts")
            print("  2. Download JSON credentials")
            print("  3. Set GOOGLE_CREDENTIALS_PATH environment variable")

    def create_or_open_sheet(self, sheet_name: str = None) -> bool:
        """Create new sheet or open existing"""
        if not self.client:
            print("❌ Not authenticated with Google Sheets")
            return False

        sheet_name = sheet_name or f"M&A Opportunities - {datetime.now().strftime('%Y-%m-%d')}"

        try:
            # Try to open existing sheet
            self.sheet = self.client.open(sheet_name)
            print(f"✓ Opened existing sheet: {sheet_name}")

        except gspread.SpreadsheetNotFound:
            # Create new sheet
            self.sheet = self.client.create(sheet_name)
            print(f"✓ Created new sheet: {sheet_name}")

            # Share with your email if specified
            share_email = os.getenv('SHEET_SHARE_EMAIL')
            if share_email:
                self.sheet.share(share_email, perm_type='user', role='writer')
                print(f"✓ Shared with {share_email}")

        return True

    def upload_listings(self, listings: List[Dict], worksheet_name: str = "Opportunities"):
        """Upload listings to worksheet"""
        if not self.sheet:
            print("❌ No sheet available")
            return

        try:
            # Get or create worksheet
            try:
                worksheet = self.sheet.worksheet(worksheet_name)
                print(f"✓ Using existing worksheet: {worksheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = self.sheet.add_worksheet(
                    title=worksheet_name,
                    rows=len(listings) + 100,
                    cols=20
                )
                print(f"✓ Created new worksheet: {worksheet_name}")

            # Define columns
            headers = [
                'Business Name',
                'City',
                'State',
                'Asking Price',
                'Revenue',
                'Cash Flow',
                'Industry',
                'Source Platform',
                'Listing URL',
                'Date Found',
                'Email Date',
                'Email Subject',
                'Status',
                'Notes'
            ]

            # Prepare data rows
            rows = [headers]

            for listing in listings:
                row = [
                    listing.get('business_name', ''),
                    listing.get('city', ''),
                    listing.get('state', ''),
                    listing.get('asking_price', ''),
                    listing.get('revenue', ''),
                    listing.get('cash_flow', ''),
                    listing.get('industry', ''),
                    listing.get('source_website', ''),
                    listing.get('listing_url', ''),
                    listing.get('date_scraped', '')[:10],  # Just date
                    listing.get('email_date', ''),
                    listing.get('email_subject', ''),
                    'New',  # Status column
                    ''  # Notes column
                ]
                rows.append(row)

            # Upload to sheet
            worksheet.clear()
            worksheet.update('A1', rows)

            # Format header row
            worksheet.format('A1:N1', {
                'textFormat': {'bold': True, 'fontSize': 11},
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7},
                'horizontalAlignment': 'CENTER',
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })

            # Freeze header row
            worksheet.freeze(rows=1)

            # Auto-resize columns
            worksheet.columns_auto_resize(0, len(headers))

            # Add filter
            worksheet.set_basic_filter()

            # Add data validation for Status column
            status_options = ['New', 'Reviewing', 'Contacted', 'In Discussion', 'Pass', 'Archived']
            worksheet.data_validation(
                f'M2:M{len(listings) + 1}',
                {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [{'userEnteredValue': opt} for opt in status_options]
                    },
                    'strict': True,
                    'showCustomUi': True
                }
            )

            print(f"\n✓ Uploaded {len(listings)} listings to Google Sheets")
            print(f"✓ Sheet URL: {self.sheet.url}")

        except Exception as e:
            print(f"❌ Failed to upload: {e}")

    def append_new_listings(self, listings: List[Dict], worksheet_name: str = "Opportunities"):
        """Append new listings without duplicates"""
        if not self.sheet:
            print("❌ No sheet available")
            return

        try:
            worksheet = self.sheet.worksheet(worksheet_name)

            # Get existing URLs
            url_column = worksheet.col_values(9)  # Column I (Listing URL)
            existing_urls = set(url_column[1:])  # Skip header

            # Filter out duplicates
            new_listings = [
                listing for listing in listings
                if listing.get('listing_url') not in existing_urls
            ]

            if not new_listings:
                print("ℹ No new listings to add (all are duplicates)")
                return

            print(f"✓ Found {len(new_listings)} new listings (filtered {len(listings) - len(new_listings)} duplicates)")

            # Prepare rows
            rows = []
            for listing in new_listings:
                row = [
                    listing.get('business_name', ''),
                    listing.get('city', ''),
                    listing.get('state', ''),
                    listing.get('asking_price', ''),
                    listing.get('revenue', ''),
                    listing.get('cash_flow', ''),
                    listing.get('industry', ''),
                    listing.get('source_website', ''),
                    listing.get('listing_url', ''),
                    listing.get('date_scraped', '')[:10],
                    listing.get('email_date', ''),
                    listing.get('email_subject', ''),
                    'New',
                    ''
                ]
                rows.append(row)

            # Append rows
            worksheet.append_rows(rows)
            print(f"✓ Appended {len(new_listings)} new listings")

        except Exception as e:
            print(f"❌ Failed to append: {e}")


def main():
    """Upload listings from JSON to Google Sheets"""
    print("="*70)
    print("GOOGLE SHEETS UPLOADER")
    print("="*70)
    print("\nUploads parsed M&A listings to Google Sheets for review\n")

    # Find latest JSON file
    data_dir = 'data'
    json_files = [f for f in os.listdir(data_dir) if f.startswith('email_listings') and f.endswith('.json')]

    if not json_files:
        print("❌ No listing files found in data/ directory")
        print("\nRun email_parser.py first to generate listings")
        return

    # Use most recent file
    latest_file = sorted(json_files)[-1]
    filepath = os.path.join(data_dir, latest_file)

    print(f"📄 Loading: {filepath}")

    # Load listings
    with open(filepath, 'r') as f:
        listings = json.load(f)

    print(f"✓ Loaded {len(listings)} listings\n")

    # Initialize uploader
    uploader = SheetsUploader()

    if not uploader.client:
        print("\n⚠ Google Sheets authentication not configured")
        print("\nListings saved locally in JSON format.")
        print("You can manually import this JSON to Excel or Google Sheets.")
        return

    # Create/open sheet
    sheet_name = os.getenv('GOOGLE_SHEET_NAME', config.GOOGLE_SHEET_NAME)

    if uploader.create_or_open_sheet(sheet_name):
        # Upload listings
        uploader.upload_listings(listings)

        print(f"\n{'='*70}")
        print("SUCCESS!")
        print(f"{'='*70}")
        print(f"\n✓ {len(listings)} opportunities uploaded to Google Sheets")
        print(f"✓ Open your sheet to review: {uploader.sheet.url}")
        print(f"\nFeatures:")
        print(f"  • Sortable and filterable")
        print(f"  • Status tracking (New, Reviewing, Contacted, etc.)")
        print(f"  • Notes column for comments")
        print(f"  • Direct links to listings")
        print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
