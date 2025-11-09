#!/usr/bin/env python3
"""
Test script to inspect BizBuySell website structure
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def test_bizbuysell():
    """Test BizBuySell scraping and save HTML for inspection"""

    print("Setting up Chrome driver...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"❌ Failed to initialize Chrome: {e}")
        print("\nTrying to install chromium and chromedriver...")
        import subprocess
        subprocess.run(['apt-get', 'update'], check=False)
        subprocess.run(['apt-get', 'install', '-y', 'chromium-browser', 'chromium-chromedriver'], check=False)

        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e2:
            print(f"❌ Still failed: {e2}")
            return

    print("✓ Chrome driver initialized")

    # Test URL - California businesses
    test_url = "https://www.bizbuysell.com/california-businesses-for-sale/"

    print(f"\nFetching: {test_url}")
    driver.get(test_url)
    time.sleep(5)  # Wait for page to fully load

    print("✓ Page loaded")

    # Get page source
    html = driver.page_source

    # Save to file for inspection
    with open('data/bizbuysell_test.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Saved HTML to data/bizbuysell_test.html")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    print("\n" + "="*70)
    print("PAGE STRUCTURE ANALYSIS")
    print("="*70)

    # Look for common listing container patterns
    print("\nSearching for listing containers...")

    patterns = [
        ('div.business-card', soup.find_all('div', class_='business-card')),
        ('div.listing', soup.find_all('div', class_='listing')),
        ('article', soup.find_all('article')),
        ('div[data-listing]', soup.find_all('div', attrs={'data-listing': True})),
        ('div.result', soup.find_all('div', class_='result')),
        ('div.search-result', soup.find_all('div', class_='search-result')),
    ]

    for pattern_name, elements in patterns:
        if elements:
            print(f"\n✓ Found {len(elements)} elements matching: {pattern_name}")

            # Show first element structure
            if len(elements) > 0:
                first = elements[0]
                print(f"\nFirst element preview:")
                print(f"  Classes: {first.get('class', [])}")
                print(f"  Attributes: {list(first.attrs.keys())}")

                # Look for title
                title = first.find(['h1', 'h2', 'h3', 'h4'])
                if title:
                    print(f"  Title found: {title.get_text(strip=True)[:60]}")

                # Look for links
                links = first.find_all('a', href=True)
                if links:
                    print(f"  Links found: {len(links)}")
                    print(f"  First link: {links[0].get('href', '')[:60]}")

                # Show snippet of text content
                text = first.get_text(strip=True)
                print(f"  Text content preview: {text[:200]}...")

    # Look for any divs with "business" in class name
    print("\n\nSearching for divs with 'business' in class name...")
    business_divs = soup.find_all('div', class_=lambda x: x and 'business' in str(x).lower())
    print(f"Found {len(business_divs)} divs with 'business' in class")

    if business_divs:
        classes = set()
        for div in business_divs[:20]:
            classes.update(div.get('class', []))
        print(f"Unique classes: {sorted(classes)}")

    # Show page title
    title = soup.find('title')
    if title:
        print(f"\nPage title: {title.get_text()}")

    # Check for anti-bot protection
    if 'cloudflare' in html.lower() or 'challenge' in html.lower():
        print("\n⚠ WARNING: Cloudflare or bot challenge detected!")

    driver.quit()
    print("\n✓ Test complete")

if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    test_bizbuysell()
