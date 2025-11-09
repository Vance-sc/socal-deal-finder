#!/usr/bin/env python3
"""
Demo of M&A Deal Finder with mock data
Shows how the system works end-to-end
"""

import json
import os
from datetime import datetime
from scraper import DealFinder, BaseScraper
from typing import List, Dict
import config


class MockBizBuySellScraper(BaseScraper):
    """Mock scraper with sample data to demonstrate functionality"""

    def __init__(self):
        super().__init__('BizBuySell (Demo)')

    def scrape(self) -> List[Dict]:
        """Return mock listing data"""

        # Mock listings with realistic data
        mock_listings = [
            {
                'business_name': 'Established HVAC Service Company',
                'city': 'San Diego',
                'state': 'CA',
                'asking_price': '$2,500,000',
                'revenue': '$3,200,000',
                'cash_flow': '$450,000',
                'ebitda': '$450,000',
                'industry': 'HVAC Services',
                'business_type': 'Service',
                'description': 'Well-established HVAC service company serving residential and commercial clients. Strong recurring maintenance contracts, excellent reputation in the community.',
                'listing_url': 'https://www.bizbuysell.com/example-listing-1',
                'year_established': '2005',
                'employees': '12',
                'reason_for_sale': 'Retirement'
            },
            {
                'business_name': 'Commercial Cleaning Service',
                'city': 'Phoenix',
                'state': 'AZ',
                'asking_price': '$1,800,000',
                'revenue': '$2,500,000',
                'cash_flow': '$350,000',
                'ebitda': '$350,000',
                'industry': 'Cleaning Services',
                'business_type': 'Service',
                'description': 'Commercial cleaning company with long-term contracts with office buildings and medical facilities. Recurring revenue model with low employee turnover.',
                'listing_url': 'https://www.bizbuysell.com/example-listing-2',
                'year_established': '2010',
                'employees': '25',
                'reason_for_sale': 'Relocation'
            },
            {
                'business_name': 'Premium Restaurant & Bar',
                'city': 'Los Angeles',
                'state': 'CA',
                'asking_price': '$3,000,000',
                'revenue': '$4,500,000',
                'cash_flow': '$600,000',
                'ebitda': '$600,000',
                'industry': 'Restaurant',
                'business_type': 'Food Service',
                'description': 'High-end restaurant in prime location. Award-winning chef, excellent reviews.',
                'listing_url': 'https://www.bizbuysell.com/example-listing-3',
                'year_established': '2015',
                'employees': '30',
                'reason_for_sale': 'Owner wants to pursue other ventures'
            },
            {
                'business_name': 'Plumbing & Drain Service',
                'city': 'Irvine',
                'state': 'CA',
                'asking_price': '$1,200,000',
                'revenue': '$1,800,000',
                'cash_flow': '$280,000',
                'ebitda': '$280,000',
                'industry': 'Plumbing Services',
                'business_type': 'Service',
                'description': 'Residential and commercial plumbing company. Strong customer base, good online reviews. Emergency service available 24/7.',
                'listing_url': 'https://www.bizbuysell.com/example-listing-4',
                'year_established': '2008',
                'employees': '8',
                'reason_for_sale': 'Retirement'
            },
            {
                'business_name': 'Digital Marketing Agency',
                'city': 'Austin',
                'state': 'TX',
                'asking_price': '$900,000',
                'revenue': '$1,500,000',
                'cash_flow': '$320,000',
                'ebitda': '$320,000',
                'industry': 'Marketing Services',
                'business_type': 'Digital Service',
                'description': 'Full-service digital marketing agency. Remote team, low overhead. Strong client retention.',
                'listing_url': 'https://www.bizbuysell.com/example-listing-5',
                'year_established': '2018',
                'employees': '6',
                'reason_for_sale': 'Partner buyout'
            },
            {
                'business_name': 'Landscaping & Maintenance Company',
                'city': 'Las Vegas',
                'state': 'NV',
                'asking_price': '$2,200,000',
                'revenue': '$3,500,000',
                'cash_flow': '$400,000',
                'ebitda': '$400,000',
                'industry': 'Landscaping Services',
                'business_type': 'Service',
                'description': 'Commercial landscaping company serving HOAs, hotels, and commercial properties. Monthly recurring contracts. Well-maintained equipment fleet.',
                'listing_url': 'https://www.bizbuysell.com/example-listing-6',
                'year_established': '2012',
                'employees': '18',
                'reason_for_sale': 'Owner health issues'
            }
        ]

        # Normalize all listings
        normalized_listings = []
        for listing in mock_listings:
            normalized = self.normalize_listing(listing)
            normalized_listings.append(normalized)

        return normalized_listings

    def parse_listing(self, element):
        """Not used in mock scraper"""
        pass


def main():
    """Run demo"""
    print("="*70)
    print("SoCal M&A Deal Finder - DEMO MODE")
    print("Using mock data to demonstrate functionality")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nAcquisition Criteria:")
    print(f"  Revenue: ${config.ACQUISITION_CRITERIA['revenue_min']:,} - "
          f"${config.ACQUISITION_CRITERIA['revenue_max']:,}")
    print(f"  Min EBITDA: ${config.ACQUISITION_CRITERIA['ebitda_min']:,}")
    print(f"  Target States: {', '.join(config.ACQUISITION_CRITERIA['target_states'])}")
    print(f"  Excluded Types: {', '.join(config.ACQUISITION_CRITERIA['excluded_types'])}")
    print()

    # Initialize deal finder
    finder = DealFinder()

    # Add mock scraper
    finder.add_scraper(MockBizBuySellScraper())

    # Run the scraping
    listings = finder.run()

    # Save results
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{config.OUTPUT_DIR}/demo_deals_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(listings, f, indent=2)

    print(f"\n✓ Saved results to {filename}")

    # Print detailed results
    print(f"\n{'='*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*70}\n")

    print(f"Total listings found: {len(listings)}")

    # Group by state
    by_state = {}
    for listing in listings:
        state = listing.get('state', 'Unknown')
        by_state.setdefault(state, []).append(listing)

    for state in sorted(by_state.keys()):
        print(f"\n{state}: {len(by_state[state])} qualified listings")

        for i, listing in enumerate(by_state[state], 1):
            print(f"\n  {i}. {listing.get('business_name', 'N/A')}")
            print(f"     Location: {listing.get('city', 'N/A')}, {state}")
            print(f"     Asking Price: {listing.get('asking_price', 'N/A')}")
            print(f"     Revenue: {listing.get('revenue', 'N/A')}")
            print(f"     Cash Flow: {listing.get('cash_flow', 'N/A')}")
            print(f"     Industry: {listing.get('industry', 'N/A')}")
            print(f"     Established: {listing.get('year_established', 'N/A')}")
            print(f"     Employees: {listing.get('employees', 'N/A')}")
            print(f"     Reason for Sale: {listing.get('reason_for_sale', 'N/A')}")
            print(f"     URL: {listing.get('listing_url', 'N/A')}")

    print(f"\n{'='*70}")
    print(f"✓ Demo Complete!")
    print(f"{'='*70}\n")

    print("NOTES:")
    print("- This demo uses mock data to show system functionality")
    print("- Restaurant listing was EXCLUDED (matches exclusion criteria)")
    print("- Digital Marketing Agency was EXCLUDED (digital-only business)")
    print("- All other listings PASSED criteria filters")
    print("\nNext steps: Implement real website scraping (see SCRAPING_SOLUTIONS.md)")


if __name__ == '__main__':
    main()
