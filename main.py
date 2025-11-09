#!/usr/bin/env python3
"""
Main entry point for SoCal M&A Deal Finder
"""

import os
import json
from datetime import datetime
from scraper import DealFinder
from scrapers import BizBuySellScraper
import config


def save_to_json(listings: list, filename: str = None):
    """Save listings to JSON file"""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config.OUTPUT_DIR}/deals_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(listings, f, indent=2)

    print(f"\n✓ Saved results to {filename}")
    return filename


def print_summary(listings: list):
    """Print summary of findings"""
    if not listings:
        print("\nNo qualified listings found.")
        return

    print(f"\n{'='*70}")
    print(f"QUALIFIED LISTINGS SUMMARY ({len(listings)} total)")
    print(f"{'='*70}\n")

    # Group by state
    by_state = {}
    for listing in listings:
        state = listing.get('state', 'Unknown')
        by_state.setdefault(state, []).append(listing)

    for state in sorted(by_state.keys()):
        print(f"\n{state}: {len(by_state[state])} listings")
        for i, listing in enumerate(by_state[state][:3], 1):  # Show first 3
            print(f"  {i}. {listing.get('business_name', 'N/A')}")
            print(f"     Price: {listing.get('asking_price', 'N/A')} | "
                  f"Revenue: {listing.get('revenue', 'N/A')} | "
                  f"CF: {listing.get('cash_flow', 'N/A')}")
            print(f"     {listing.get('city', 'N/A')}, {state}")

        if len(by_state[state]) > 3:
            print(f"  ... and {len(by_state[state]) - 3} more")


def main():
    """Main execution"""
    print("="*70)
    print("SoCal M&A Deal Finder")
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

    # Add scrapers (starting with BizBuySell)
    finder.add_scraper(BizBuySellScraper())

    # TODO: Add more scrapers as they're implemented
    # finder.add_scraper(BizQuestScraper())
    # finder.add_scraper(BizBenScraper())

    # Run the scraping
    try:
        listings = finder.run()

        # Save results
        if listings:
            output_file = save_to_json(listings)

            # Print summary
            print_summary(listings)

            print(f"\n{'='*70}")
            print(f"✓ Complete! Found {len(listings)} qualified opportunities")
            print(f"  Results saved to: {output_file}")
            print(f"{'='*70}\n")

            return listings

        else:
            print("\n⚠ No qualified listings found matching criteria")
            print("This may be due to:")
            print("  1. No listings currently match the criteria")
            print("  2. Website HTML structure has changed (needs scraper update)")
            print("  3. Network/rate limiting issues\n")

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == '__main__':
    main()
