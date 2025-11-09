"""
Google Cloud integrations for Sheets and Gmail
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


class GoogleSheetsManager:
    """Manager for Google Sheets operations"""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets manager

        Args:
            credentials_path: Path to service account JSON credentials
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.client = None
        self.sheet = None

        if self.credentials_path and os.path.exists(self.credentials_path):
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API"""
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
            print(f"⚠ Failed to authenticate with Google Sheets: {e}")

    def get_or_create_sheet(self, sheet_name: str = None) -> Optional[gspread.Spreadsheet]:
        """
        Get existing sheet or create new one

        Args:
            sheet_name: Name of the spreadsheet

        Returns:
            Spreadsheet object or None
        """
        if not self.client:
            print("⚠ Not authenticated with Google Sheets")
            return None

        sheet_name = sheet_name or config.GOOGLE_SHEET_NAME

        try:
            # Try to open existing sheet
            self.sheet = self.client.open(sheet_name)
            print(f"✓ Opened existing sheet: {sheet_name}")

        except gspread.SpreadsheetNotFound:
            # Create new sheet
            try:
                self.sheet = self.client.create(sheet_name)
                print(f"✓ Created new sheet: {sheet_name}")

                # Share with your email if specified
                email = os.getenv('SHEET_SHARE_EMAIL')
                if email:
                    self.sheet.share(email, perm_type='user', role='writer')
                    print(f"✓ Shared sheet with {email}")

            except Exception as e:
                print(f"❌ Failed to create sheet: {e}")
                return None

        return self.sheet

    def save_listings(self, listings: List[Dict], worksheet_name: str = "Listings"):
        """
        Save listings to Google Sheet

        Args:
            listings: List of listing dictionaries
            worksheet_name: Name of the worksheet
        """
        if not self.sheet:
            print("⚠ No sheet available. Call get_or_create_sheet() first")
            return

        try:
            # Get or create worksheet
            try:
                worksheet = self.sheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.sheet.add_worksheet(
                    title=worksheet_name,
                    rows=len(listings) + 100,
                    cols=len(config.LISTING_FIELDS)
                )

            # Prepare data
            headers = config.LISTING_FIELDS
            rows = [headers]

            for listing in listings:
                row = [str(listing.get(field, '')) for field in headers]
                rows.append(row)

            # Clear and update
            worksheet.clear()
            worksheet.update('A1', rows)

            # Format header row
            worksheet.format('A1:Z1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

            print(f"✓ Saved {len(listings)} listings to Google Sheet")

        except Exception as e:
            print(f"❌ Failed to save to Google Sheet: {e}")

    def get_existing_listing_ids(self, worksheet_name: str = "Listings") -> set:
        """
        Get set of existing listing IDs from sheet

        Args:
            worksheet_name: Name of the worksheet

        Returns:
            Set of listing IDs
        """
        if not self.sheet:
            return set()

        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            # Get listing_id column (assuming it's first column)
            ids = worksheet.col_values(1)[1:]  # Skip header
            return set(ids)

        except Exception as e:
            print(f"⚠ Failed to get existing IDs: {e}")
            return set()

    def append_new_listings(self, listings: List[Dict], worksheet_name: str = "Listings"):
        """
        Append only new listings to sheet (avoiding duplicates)

        Args:
            listings: List of listing dictionaries
            worksheet_name: Name of the worksheet
        """
        existing_ids = self.get_existing_listing_ids(worksheet_name)

        new_listings = [
            listing for listing in listings
            if listing.get('listing_id') not in existing_ids
        ]

        if new_listings:
            print(f"Found {len(new_listings)} new listings to add")

            try:
                worksheet = self.sheet.worksheet(worksheet_name)

                rows = []
                for listing in new_listings:
                    row = [str(listing.get(field, '')) for field in config.LISTING_FIELDS]
                    rows.append(row)

                worksheet.append_rows(rows)
                print(f"✓ Appended {len(new_listings)} new listings")

            except Exception as e:
                print(f"❌ Failed to append listings: {e}")
        else:
            print("No new listings to add (all already exist)")


class GmailManager:
    """Manager for Gmail API operations"""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Gmail manager

        Args:
            credentials_path: Path to OAuth credentials JSON
        """
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH')
        self.service = None

        if self.credentials_path and os.path.exists(self.credentials_path):
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        try:
            scopes = ['https://www.googleapis.com/auth/gmail.send']

            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )

            self.service = build('gmail', 'v1', credentials=credentials)
            print("✓ Authenticated with Gmail")

        except Exception as e:
            print(f"⚠ Failed to authenticate with Gmail: {e}")

    def send_digest(self, listings: List[Dict], to_addresses: List[str] = None):
        """
        Send email digest of new listings

        Args:
            listings: List of listing dictionaries
            to_addresses: List of recipient email addresses
        """
        if not self.service:
            print("⚠ Gmail service not available")
            return

        to_addresses = to_addresses or config.EMAIL_TO

        if not to_addresses or not listings:
            return

        try:
            # Build email content
            subject = f"SoCal M&A Deal Finder - {len(listings)} New Opportunities"
            body = self._build_email_body(listings)

            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = config.EMAIL_FROM
            message['To'] = ', '.join(to_addresses)

            # Add HTML part
            html_part = MIMEText(body, 'html')
            message.attach(html_part)

            # Send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}

            self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            print(f"✓ Sent email digest to {len(to_addresses)} recipient(s)")

        except HttpError as e:
            print(f"❌ Failed to send email: {e}")

    def _build_email_body(self, listings: List[Dict]) -> str:
        """
        Build HTML email body

        Args:
            listings: List of listing dictionaries

        Returns:
            HTML string
        """
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #2c3e50; }}
                .listing {{
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
                .listing h3 {{ margin-top: 0; color: #34495e; }}
                .detail {{ margin: 5px 0; }}
                .label {{ font-weight: bold; }}
                a {{ color: #3498db; }}
            </style>
        </head>
        <body>
            <h2>SoCal M&A Deal Finder Report</h2>
            <p>Date: {datetime.now().strftime('%B %d, %Y')}</p>
            <p>Found <strong>{len(listings)}</strong> qualified acquisition opportunities:</p>
        """

        for i, listing in enumerate(listings[:20], 1):  # Limit to 20 in email
            html += f"""
            <div class="listing">
                <h3>{i}. {listing.get('business_name', 'N/A')}</h3>
                <div class="detail">
                    <span class="label">Location:</span>
                    {listing.get('city', 'N/A')}, {listing.get('state', 'N/A')}
                </div>
                <div class="detail">
                    <span class="label">Asking Price:</span> {listing.get('asking_price', 'N/A')}
                </div>
                <div class="detail">
                    <span class="label">Revenue:</span> {listing.get('revenue', 'N/A')}
                </div>
                <div class="detail">
                    <span class="label">Cash Flow:</span> {listing.get('cash_flow', 'N/A')}
                </div>
                <div class="detail">
                    <span class="label">Industry:</span> {listing.get('industry', 'N/A')}
                </div>
                <div class="detail">
                    <a href="{listing.get('listing_url', '#')}">View Listing →</a>
                </div>
            </div>
            """

        if len(listings) > 20:
            html += f"<p><em>... and {len(listings) - 20} more in the full report</em></p>"

        html += """
            <hr>
            <p style="color: #7f8c8d; font-size: 12px;">
                This is an automated report from SoCal M&A Deal Finder
            </p>
        </body>
        </html>
        """

        return html
