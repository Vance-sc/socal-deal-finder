#!/usr/bin/env python3
"""
Test email connection and setup
Verifies credentials and shows sample emails
"""

import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime, timedelta


def test_email_connection():
    """Test Gmail IMAP connection"""

    print("="*70)
    print("EMAIL CONNECTION TEST")
    print("="*70)
    print()

    # Get credentials
    email_address = os.getenv('ALERT_EMAIL_ADDRESS')
    password = os.getenv('ALERT_EMAIL_PASSWORD')

    if not email_address or not password:
        print("❌ ERROR: Email credentials not set")
        print()
        print("Please set environment variables:")
        print("  export ALERT_EMAIL_ADDRESS='your-email@gmail.com'")
        print("  export ALERT_EMAIL_PASSWORD='your-app-password'")
        print()
        print("For Gmail App Password:")
        print("  1. Enable 2-step verification")
        print("  2. Go to: https://myaccount.google.com/apppasswords")
        print("  3. Generate password for 'Mail'")
        print()
        return False

    print(f"Testing connection to: {email_address}")
    print()

    try:
        # Connect to Gmail
        print("[1/4] Connecting to Gmail IMAP server...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        print("     ✅ Connected")

        # Login
        print("[2/4] Authenticating...")
        mail.login(email_address, password)
        print("     ✅ Authenticated successfully")

        # Select inbox
        print("[3/4] Accessing inbox...")
        mail.select('inbox')
        print("     ✅ Inbox accessed")

        # Get recent emails
        print("[4/4] Fetching recent emails...")

        # Search for emails from last 7 days
        since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
        _, message_numbers = mail.search(None, f'SINCE {since_date}')

        if message_numbers[0]:
            msg_ids = message_numbers[0].split()
            print(f"     ✅ Found {len(msg_ids)} emails in last 7 days")

            print()
            print("="*70)
            print("RECENT EMAILS (Last 10)")
            print("="*70)
            print()

            # Show last 10 emails
            for msg_id in msg_ids[-10:]:
                _, msg_data = mail.fetch(msg_id, '(RFC822)')
                email_body = email.message_from_bytes(msg_data[0][1])

                # Decode subject
                subject = email_body['Subject']
                if subject:
                    decoded = decode_header(subject)
                    subject_str = ""
                    for content, encoding in decoded:
                        if isinstance(content, bytes):
                            subject_str += content.decode(encoding or 'utf-8', errors='ignore')
                        else:
                            subject_str += content
                else:
                    subject_str = "(No subject)"

                # Get sender
                from_addr = email_body['From']

                # Get date
                date_str = email_body['Date']

                print(f"From: {from_addr}")
                print(f"Date: {date_str}")
                print(f"Subject: {subject_str[:60]}...")
                print()

            # Check for M&A platform emails
            print("="*70)
            print("CHECKING FOR M&A PLATFORM EMAILS")
            print("="*70)
            print()

            platform_keywords = [
                'bizbuysell', 'bizquest', 'businessbroker', 'bizben',
                'dealstream', 'sunbelt', 'merger', 'transworld',
                'murphy', 'flippa', 'acquire', 'empire'
            ]

            found_platforms = set()

            for msg_id in msg_ids:
                _, msg_data = mail.fetch(msg_id, '(RFC822)')
                email_body = email.message_from_bytes(msg_data[0][1])
                from_addr = email_body['From'].lower()

                for keyword in platform_keywords:
                    if keyword in from_addr:
                        found_platforms.add(keyword)

            if found_platforms:
                print(f"✅ Found emails from {len(found_platforms)} M&A platforms:")
                for platform in sorted(found_platforms):
                    print(f"   • {platform}")
                print()
                print("🎉 Great! Email alerts are working.")
                print("   Run email_parser.py to extract listings.")
            else:
                print("⚠️  No M&A platform emails found yet")
                print()
                print("This means either:")
                print("  1. You haven't set up email alerts yet")
                print("  2. Platforms haven't sent first email yet (wait 1-2 days)")
                print("  3. Emails went to spam (check spam folder)")
                print()
                print("Next steps:")
                print("  • Set up email alerts on M&A platforms")
                print("  • Wait for first emails to arrive")
                print("  • Run this test again")

        else:
            print("     ℹ️  Inbox is empty")

        # Cleanup
        mail.close()
        mail.logout()

        print()
        print("="*70)
        print("✅ EMAIL SETUP TEST COMPLETE")
        print("="*70)
        print()
        print("Your email configuration is working correctly!")
        print()

        return True

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        print()
        print("Common issues:")
        print("  • Wrong password (use App Password, not regular password)")
        print("  • 2-step verification not enabled")
        print("  • IMAP not enabled in Gmail settings")
        print()
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    success = test_email_connection()
    exit(0 if success else 1)
