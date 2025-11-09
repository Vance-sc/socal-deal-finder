#!/usr/bin/env python3
"""
Comprehensive testing script for all 28 M&A marketplace websites
Tests accessibility and identifies which sites can be scraped
"""

import requests
import cloudscraper
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
from typing import Dict, List
import os


# Complete list of 28 M&A marketplace websites
MARKETPLACE_SITES = [
    # Priority Sites (Phase 1)
    {
        'name': 'BizBuySell',
        'url': 'https://www.bizbuysell.com/',
        'search_url': 'https://www.bizbuysell.com/california-businesses-for-sale/',
        'priority': 1
    },
    {
        'name': 'BizQuest',
        'url': 'https://www.bizquest.com/',
        'search_url': 'https://www.bizquest.com/businesses-for-sale/california/',
        'priority': 2
    },
    {
        'name': 'Business Broker Network',
        'url': 'https://www.businessbroker.net/',
        'search_url': 'https://www.businessbroker.net/businesses/california/',
        'priority': 3
    },
    {
        'name': 'BizBen',
        'url': 'https://www.bizben.com/',
        'search_url': 'https://www.bizben.com/businesses-for-sale',
        'priority': 4
    },
    {
        'name': 'Strategic Business Brokers',
        'url': 'https://www.businessbrokerphoenixaz.com/',
        'search_url': 'https://www.businessbrokerphoenixaz.com/businesses-for-sale',
        'priority': 5
    },
    {
        'name': 'DealStream',
        'url': 'https://dealstream.com/',
        'search_url': 'https://dealstream.com/businesses-for-sale/',
        'priority': 6
    },

    # Additional Sites (Phase 2)
    {
        'name': 'MergerNetwork',
        'url': 'https://www.mergernetwork.com/',
        'search_url': 'https://www.mergernetwork.com/find-business/',
        'priority': 7
    },
    {
        'name': 'Sunbelt Business Brokers',
        'url': 'https://www.sunbeltnetwork.com/',
        'search_url': 'https://www.sunbeltnetwork.com/businesses-for-sale',
        'priority': 8
    },
    {
        'name': 'BusinessesForSale.com',
        'url': 'https://www.businessesforsale.com/',
        'search_url': 'https://www.businessesforsale.com/us/',
        'priority': 9
    },
    {
        'name': 'BizEx',
        'url': 'https://www.bizex.net/',
        'search_url': 'https://www.bizex.net/businesses-for-sale/',
        'priority': 10
    },
    {
        'name': 'BusinessMart',
        'url': 'https://www.businessmart.com/',
        'search_url': 'https://www.businessmart.com/businesses-for-sale/',
        'priority': 11
    },
    {
        'name': 'VR Business Brokers',
        'url': 'https://www.vrbbusinessbrokers.com/',
        'search_url': 'https://www.vrbbusinessbrokers.com/businesses-for-sale',
        'priority': 12
    },
    {
        'name': 'Murphy Business',
        'url': 'https://www.murphybusiness.com/',
        'search_url': 'https://www.murphybusiness.com/businesses-for-sale',
        'priority': 13
    },
    {
        'name': 'Transworld Business Advisors',
        'url': 'https://www.tworld.com/',
        'search_url': 'https://www.tworld.com/businesses-for-sale/',
        'priority': 14
    },
    {
        'name': 'BizBroker24',
        'url': 'https://www.bizbroker24.com/',
        'search_url': 'https://www.bizbroker24.com/businesses-for-sale',
        'priority': 15
    },
    {
        'name': 'LoopNet (Commercial)',
        'url': 'https://www.loopnet.com/',
        'search_url': 'https://www.loopnet.com/search/businesses-for-sale/',
        'priority': 16
    },
    {
        'name': 'BusinessBroker.com',
        'url': 'https://www.businessbroker.com/',
        'search_url': 'https://www.businessbroker.com/businesses-for-sale',
        'priority': 17
    },
    {
        'name': 'Acquire.com',
        'url': 'https://acquire.com/',
        'search_url': 'https://acquire.com/startups',
        'priority': 18
    },
    {
        'name': 'Flippa',
        'url': 'https://flippa.com/',
        'search_url': 'https://flippa.com/search?filter=business',
        'priority': 19
    },
    {
        'name': 'BizOffers',
        'url': 'https://www.bizoffers.com/',
        'search_url': 'https://www.bizoffers.com/businesses-for-sale',
        'priority': 20
    },
    {
        'name': 'IBBA Marketplace',
        'url': 'https://www.ibba.org/',
        'search_url': 'https://www.ibba.org/find-a-business-broker/',
        'priority': 21
    },
    {
        'name': 'Axial Network',
        'url': 'https://www.axial.net/',
        'search_url': 'https://www.axial.net/',
        'priority': 22
    },
    {
        'name': 'BusinessesForSale.com',
        'url': 'https://www.businessesforsale.com/',
        'search_url': 'https://www.businessesforsale.com/us/search/',
        'priority': 23
    },
    {
        'name': 'BuySellBusiness.com',
        'url': 'https://www.buysellbusiness.com/',
        'search_url': 'https://www.buysellbusiness.com/businesses-for-sale',
        'priority': 24
    },
    {
        'name': 'MicroAcquire',
        'url': 'https://microacquire.com/',
        'search_url': 'https://microacquire.com/startups',
        'priority': 25
    },
    {
        'name': 'Empire Flippers',
        'url': 'https://empireflippers.com/',
        'search_url': 'https://empireflippers.com/marketplace/',
        'priority': 26
    },
    {
        'name': 'FE International',
        'url': 'https://feinternational.com/',
        'search_url': 'https://feinternational.com/buy-a-website/',
        'priority': 27
    },
    {
        'name': 'Quiet Light',
        'url': 'https://quietlight.com/',
        'search_url': 'https://quietlight.com/listings/',
        'priority': 28
    }
]


class SiteTester:
    """Test M&A marketplace sites for accessibility"""

    def __init__(self):
        self.results = []
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )

    def test_site(self, site: Dict) -> Dict:
        """Test a single site with multiple methods"""

        print(f"\n{'='*70}")
        print(f"Testing: {site['name']} (Priority {site['priority']})")
        print(f"{'='*70}")

        result = {
            'name': site['name'],
            'url': site['url'],
            'search_url': site['search_url'],
            'priority': site['priority'],
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

        # Test 1: Basic requests library
        print("\n[1/3] Testing with standard HTTP requests...")
        result['tests']['basic_http'] = self._test_basic_http(site['search_url'])

        # Test 2: Cloudscraper (Cloudflare bypass)
        print("[2/3] Testing with cloudscraper...")
        result['tests']['cloudscraper'] = self._test_cloudscraper(site['search_url'])

        # Test 3: Analyze HTML structure (if accessible)
        if result['tests']['basic_http']['accessible'] or result['tests']['cloudscraper']['accessible']:
            print("[3/3] Analyzing page structure...")
            html = result['tests']['cloudscraper'].get('html') or result['tests']['basic_http'].get('html')
            result['tests']['structure'] = self._analyze_structure(html)
        else:
            print("[3/3] Skipped (site not accessible)")
            result['tests']['structure'] = {'analyzed': False, 'reason': 'Site not accessible'}

        # Summary
        result['accessible'] = (
            result['tests']['basic_http']['accessible'] or
            result['tests']['cloudscraper']['accessible']
        )
        result['recommended_method'] = self._get_recommended_method(result['tests'])

        # Print summary
        self._print_summary(result)

        return result

    def _test_basic_http(self, url: str) -> Dict:
        """Test with basic HTTP request"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)

            accessible = response.status_code == 200

            return {
                'accessible': accessible,
                'status_code': response.status_code,
                'content_length': len(response.content) if accessible else 0,
                'html': response.text if accessible else None,
                'error': None if accessible else f"Status {response.status_code}"
            }

        except Exception as e:
            return {
                'accessible': False,
                'status_code': None,
                'content_length': 0,
                'html': None,
                'error': str(e)
            }

    def _test_cloudscraper(self, url: str) -> Dict:
        """Test with cloudscraper"""
        try:
            response = self.scraper.get(url, timeout=15)

            accessible = response.status_code == 200

            return {
                'accessible': accessible,
                'status_code': response.status_code,
                'content_length': len(response.content) if accessible else 0,
                'html': response.text if accessible else None,
                'error': None if accessible else f"Status {response.status_code}"
            }

        except Exception as e:
            return {
                'accessible': False,
                'status_code': None,
                'content_length': 0,
                'html': None,
                'error': str(e)
            }

    def _analyze_structure(self, html: str) -> Dict:
        """Analyze HTML structure for listing containers"""
        if not html:
            return {'analyzed': False}

        soup = BeautifulSoup(html, 'lxml')

        analysis = {
            'analyzed': True,
            'page_title': soup.find('title').get_text() if soup.find('title') else 'N/A',
            'has_cloudflare': 'cloudflare' in html.lower(),
            'potential_containers': []
        }

        # Look for common listing container patterns
        patterns = [
            ('div.business', 'business' in ' '.join(div.get('class', [])).lower() if div.get('class') else False)
            for div in soup.find_all('div', class_=True)
        ]

        # Check for common class patterns
        class_patterns = ['listing', 'business', 'result', 'card', 'item', 'opportunity']

        for pattern in class_patterns:
            elements = soup.find_all(class_=lambda x: x and pattern in str(x).lower())
            if elements:
                analysis['potential_containers'].append({
                    'pattern': pattern,
                    'count': len(elements),
                    'sample_classes': list(set([' '.join(e.get('class', [])) for e in elements[:3]]))
                })

        return analysis

    def _get_recommended_method(self, tests: Dict) -> str:
        """Determine best scraping method"""
        if tests['basic_http']['accessible']:
            return 'basic_http'
        elif tests['cloudscraper']['accessible']:
            return 'cloudscraper'
        else:
            return 'selenium_required_or_blocked'

    def _print_summary(self, result: Dict):
        """Print test summary"""
        print(f"\n{'─'*70}")
        print("RESULTS:")

        if result['accessible']:
            print(f"  ✅ ACCESSIBLE via {result['recommended_method']}")

            if result['tests']['structure']['analyzed']:
                containers = result['tests']['structure']['potential_containers']
                if containers:
                    print(f"  📦 Found {len(containers)} potential listing container types:")
                    for c in containers[:3]:
                        print(f"     - {c['pattern']}: {c['count']} elements")
                else:
                    print(f"  ⚠️  No obvious listing containers found (may need manual inspection)")
        else:
            print(f"  ❌ BLOCKED - {result['recommended_method']}")
            basic_error = result['tests']['basic_http'].get('error', 'Unknown')
            cloud_error = result['tests']['cloudscraper'].get('error', 'Unknown')
            print(f"     Basic HTTP: {basic_error}")
            print(f"     Cloudscraper: {cloud_error}")

        time.sleep(1)  # Rate limiting between sites

    def run_all_tests(self):
        """Test all sites"""
        print(f"\n{'#'*70}")
        print(f"# M&A MARKETPLACE ACCESSIBILITY TEST")
        print(f"# Testing {len(MARKETPLACE_SITES)} websites")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}")

        for site in MARKETPLACE_SITES:
            result = self.test_site(site)
            self.results.append(result)
            time.sleep(2)  # Rate limit between sites

        return self.results

    def save_results(self):
        """Save test results to file"""
        os.makedirs('data', exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/site_test_results_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Full results saved to: {filename}")

        return filename

    def print_final_report(self):
        """Print comprehensive final report"""
        accessible = [r for r in self.results if r['accessible']]
        blocked = [r for r in self.results if not r['accessible']]

        print(f"\n\n{'='*70}")
        print("FINAL REPORT")
        print(f"{'='*70}\n")

        print(f"📊 SUMMARY:")
        print(f"   Total Sites Tested: {len(self.results)}")
        print(f"   ✅ Accessible: {len(accessible)} ({len(accessible)/len(self.results)*100:.1f}%)")
        print(f"   ❌ Blocked: {len(blocked)} ({len(blocked)/len(self.results)*100:.1f}%)")

        if accessible:
            print(f"\n✅ ACCESSIBLE SITES (Ready to scrape):")
            print(f"{'─'*70}")
            for r in sorted(accessible, key=lambda x: x['priority']):
                method = "Basic HTTP" if r['recommended_method'] == 'basic_http' else "Cloudscraper"
                containers = len(r['tests']['structure'].get('potential_containers', []))
                print(f"  {r['priority']:2d}. {r['name']:<35} [{method}]")
                if containers > 0:
                    print(f"      └─ {containers} potential container types found")

        if blocked:
            print(f"\n❌ BLOCKED SITES (Need alternative approach):")
            print(f"{'─'*70}")
            for r in sorted(blocked, key=lambda x: x['priority']):
                print(f"  {r['priority']:2d}. {r['name']}")

        print(f"\n{'='*70}")
        print("RECOMMENDATIONS:")
        print(f"{'='*70}")

        if len(accessible) > 0:
            print(f"\n1. START HERE - Implement scrapers for these {len(accessible)} accessible sites:")
            for r in accessible[:5]:
                print(f"   • {r['name']}")
            if len(accessible) > 5:
                print(f"   ... and {len(accessible) - 5} more")

        if len(blocked) > 0:
            print(f"\n2. FOR BLOCKED SITES - Try these approaches:")
            print(f"   • Set up email alerts")
            print(f"   • Contact for official API access")
            print(f"   • Use ScraperAPI or similar service")
            print(f"   • Try Selenium with undetected-chromedriver")

        print(f"\n3. NEXT STEPS:")
        print(f"   • Review HTML structure in saved results")
        print(f"   • Implement scraper for easiest accessible site first")
        print(f"   • Test with real data extraction")
        print(f"   • Deploy and automate")

        print(f"\n{'='*70}\n")


def main():
    """Run comprehensive site testing"""
    tester = SiteTester()

    # Run all tests
    tester.run_all_tests()

    # Save results
    tester.save_results()

    # Print final report
    tester.print_final_report()


if __name__ == '__main__':
    main()
