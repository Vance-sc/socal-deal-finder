#!/usr/bin/env python3
"""
Test BizBuySell access with cloudscraper (Cloudflare bypass)
"""

import cloudscraper
from bs4 import BeautifulSoup
import json

def test_bizbuysell_access():
    """Test accessing BizBuySell with cloudscraper"""

    print("Testing BizBuySell access with cloudscraper...")
    print("="*70)

    # Create scraper that can bypass Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    # Test URLs
    test_urls = [
        "https://www.bizbuysell.com/",
        "https://www.bizbuysell.com/california-businesses-for-sale/",
        "https://www.bizbuysell.com/businesses-for-sale/california/",
    ]

    for url in test_urls:
        print(f"\nTrying: {url}")
        try:
            response = scraper.get(url, timeout=15)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print(f"  ✓ Success! Content length: {len(response.content)}")

                # Parse and analyze
                soup = BeautifulSoup(response.content, 'lxml')

                # Save HTML for inspection
                filename = f"data/bizbuysell_{url.split('/')[-2] or 'home'}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  ✓ Saved to {filename}")

                # Analyze structure
                print(f"\n  Page title: {soup.find('title').get_text() if soup.find('title') else 'N/A'}")

                # Look for listing containers
                patterns = [
                    ('div with "business" class', soup.find_all('div', class_=lambda x: x and 'business' in str(x).lower())),
                    ('div with "listing" class', soup.find_all('div', class_=lambda x: x and 'listing' in str(x).lower())),
                    ('article tags', soup.find_all('article')),
                    ('div with "card" class', soup.find_all('div', class_=lambda x: x and 'card' in str(x).lower())),
                ]

                for pattern_name, elements in patterns:
                    if elements:
                        print(f"  ✓ Found {len(elements)} {pattern_name}")

                        if len(elements) > 0:
                            first = elements[0]
                            classes = first.get('class', [])
                            print(f"    First element classes: {classes}")

                            # Look for title
                            title = first.find(['h1', 'h2', 'h3', 'h4'])
                            if title:
                                print(f"    Sample title: {title.get_text(strip=True)[:60]}...")

                # Find all unique class names that might be listings
                all_divs = soup.find_all('div', class_=True)
                class_names = set()
                for div in all_divs:
                    classes = div.get('class', [])
                    class_names.update(classes)

                business_classes = [c for c in class_names if any(keyword in c.lower() for keyword in ['business', 'listing', 'result', 'card', 'item'])]
                if business_classes:
                    print(f"\n  Potential listing classes:")
                    for cls in sorted(business_classes)[:10]:
                        print(f"    - {cls}")

                break  # Stop after first successful URL

            else:
                print(f"  ✗ Failed with status {response.status_code}")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "="*70)
    print("Test complete. Check data/ directory for saved HTML files.")

if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    test_bizbuysell_access()
