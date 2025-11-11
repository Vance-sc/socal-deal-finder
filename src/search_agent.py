"""
AI-Powered Search Agent using Anthropic Claude API with web search.

This module handles intelligent searching of M&A marketplace websites
using Claude's built-in web search capability.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re

from anthropic import Anthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import structlog

logger = structlog.get_logger()


class SearchAgent:
    """
    AI-powered search agent that finds M&A opportunities using Claude API.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize search agent.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.client = Anthropic(api_key=config["anthropic_api_key"])
        self.model = "claude-3-5-sonnet-20240620"  # Claude 3.5 Sonnet with web search
        self.criteria = config["criteria"]
        self.max_tokens = 4096

    def build_search_query(self, site: Dict[str, Any]) -> str:
        """
        Build intelligent search query for a specific site.

        Args:
            site: Site configuration dictionary

        Returns:
            Search query string
        """
        domain = site["domain"]
        criteria = self.criteria

        # Extract criteria
        revenue_min = self.config["criteria"]["revenue"]["min"]
        revenue_max = self.config["criteria"]["revenue"]["max"]
        cash_flow_min = self.config["criteria"]["cash_flow"]["min"]
        states = ", ".join(criteria["target_states"])
        lookback_days = self.config["search_lookback_days"]

        # Build query
        query = f"""
Search the website {domain} for businesses for sale that match these criteria:

FINANCIAL REQUIREMENTS:
- Annual revenue: ${revenue_min:,} - ${revenue_max:,}
- Minimum cash flow/EBITDA/SDE: ${cash_flow_min:,}

LOCATION REQUIREMENTS:
- States: {states}
- Priority regions: Southern California, Orange County, San Diego, Phoenix, Las Vegas

BUSINESS TYPE REQUIREMENTS:
- Service-based businesses with recurring or repeat revenue
- Essential services, B2B services, healthcare services, professional services, home services
- Local market presence with operational upside potential

MUST EXCLUDE:
- Restaurants, bars, cafes, food trucks, or any food service businesses
- Franchises (with franchise fees or royalty payments)
- Digital-only businesses, e-commerce without services, online courses
- Heavy manufacturing

SEARCH SCOPE:
- Focus on listings from the last {lookback_days} days
- Find up to {self.config['max_results_per_site']} relevant businesses

For each matching business, extract and provide:
1. Business name (or type if name is not disclosed)
2. Specific location (city and state)
3. Asking price
4. Annual revenue
5. Cash flow / EBITDA / SDE (use whatever term the listing uses)
6. Business type / industry
7. Brief description (2-3 sentences highlighting key features)
8. Direct URL to the listing
9. Why it matches our criteria (explain the fit)
10. Confidence score (0-100%) indicating how well it matches our criteria

Format each result as a JSON object with these fields:
{{
  "business_name": "...",
  "city": "...",
  "state": "...",
  "asking_price": 0,
  "revenue": 0,
  "cash_flow": 0,
  "industry": "...",
  "description": "...",
  "url": "...",
  "match_reason": "...",
  "confidence_score": 0.0
}}

Return results as a JSON array. If no matches found, return an empty array [].
"""

        return query.strip()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    def search_site(self, site: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search a specific M&A marketplace website using Claude with web search.

        Args:
            site: Site configuration dictionary

        Returns:
            List of deals found
        """
        site_name = site["name"]
        domain = site["domain"]

        logger.info(f"Starting search", site=site_name, domain=domain)

        try:
            # Build search query
            search_query = self.build_search_query(site)

            # Call Claude API with web search
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": search_query,
                    }
                ],
            )

            # Parse response
            deals = self._parse_claude_response(response, site)

            # Filter by confidence score
            min_score = self.config["min_confidence_score"]
            filtered_deals = [
                deal for deal in deals
                if deal.get("confidence_score", 0) >= min_score
            ]

            logger.info(
                f"Search complete",
                site=site_name,
                total_found=len(deals),
                filtered=len(filtered_deals),
                min_score=min_score,
            )

            return filtered_deals

        except Exception as e:
            logger.error(f"Search failed", site=site_name, error=str(e))
            raise

    def _parse_claude_response(
        self, response: Any, site: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse Claude API response and extract deal information.

        Args:
            response: Claude API response
            site: Site configuration

        Returns:
            List of parsed deals
        """
        deals = []

        # Extract content from response
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text

                # Try to extract JSON from the response
                deals_data = self._extract_json_from_text(text)

                if deals_data:
                    for deal_data in deals_data:
                        # Add metadata
                        deal_data["source_site"] = site["name"]
                        deal_data["source_domain"] = site["domain"]
                        deal_data["date_found"] = datetime.now().isoformat()

                        # Normalize field names
                        deal = self._normalize_deal(deal_data)

                        deals.append(deal)

        return deals

    def _extract_json_from_text(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extract JSON array from Claude's text response.

        Args:
            text: Text containing JSON

        Returns:
            List of dictionaries or None
        """
        try:
            # Try direct JSON parse
            data = json.loads(text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]

        except json.JSONDecodeError:
            # Try to find JSON in text
            json_pattern = r'\[[\s\S]*\]'
            matches = re.findall(json_pattern, text)

            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        return data
                except json.JSONDecodeError:
                    continue

            # Try single object
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, text)

            for match in matches:
                try:
                    data = json.loads(match)
                    return [data]
                except json.JSONDecodeError:
                    continue

        return None

    def _normalize_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize deal data to consistent format.

        Args:
            deal_data: Raw deal data

        Returns:
            Normalized deal dictionary
        """
        return {
            "business_name": deal_data.get("business_name", "Undisclosed"),
            "city": deal_data.get("city", ""),
            "state": deal_data.get("state", ""),
            "asking_price": self._parse_currency(deal_data.get("asking_price", 0)),
            "revenue": self._parse_currency(deal_data.get("revenue", 0)),
            "cash_flow": self._parse_currency(deal_data.get("cash_flow", 0)),
            "industry": deal_data.get("industry", ""),
            "description": deal_data.get("description", ""),
            "url": deal_data.get("url", ""),
            "match_reason": deal_data.get("match_reason", ""),
            "confidence_score": float(deal_data.get("confidence_score", 0)) / 100.0,  # Convert to 0-1
            "source_site": deal_data.get("source_site", ""),
            "source_domain": deal_data.get("source_domain", ""),
            "date_found": deal_data.get("date_found", datetime.now().isoformat()),
        }

    def _parse_currency(self, value: Any) -> float:
        """
        Parse currency value to float.

        Args:
            value: Currency value (string or number)

        Returns:
            Float value
        """
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove currency symbols and commas
            value = re.sub(r'[$,]', '', value)

            # Handle K (thousands) and M (millions)
            if 'K' in value.upper():
                return float(value.upper().replace('K', '')) * 1_000
            elif 'M' in value.upper():
                return float(value.upper().replace('M', '')) * 1_000_000

            try:
                return float(value)
            except ValueError:
                return 0.0

        return 0.0

    def search_all_sites(self) -> List[Dict[str, Any]]:
        """
        Search all enabled sites.

        Returns:
            Combined list of all deals found
        """
        from .utils import get_enabled_sites, deduplicate_results

        enabled_sites = get_enabled_sites(self.config)

        logger.info(f"Starting search across {len(enabled_sites)} sites")

        all_deals = []

        for i, site in enumerate(enabled_sites, 1):
            try:
                deals = self.search_site(site)
                all_deals.extend(deals)

                # Rate limiting - small delay between sites
                if i < len(enabled_sites):
                    time.sleep(self.config["retry_delay_seconds"])

            except Exception as e:
                logger.error(f"Failed to search site", site=site["name"], error=str(e))
                # Continue with other sites
                continue

        # Deduplicate results
        unique_deals = deduplicate_results(all_deals)

        logger.info(
            "Search complete across all sites",
            total_found=len(all_deals),
            unique=len(unique_deals),
        )

        return unique_deals


if __name__ == "__main__":
    # Test the search agent with BizBuySell
    from utils import load_config, setup_logging, print_banner

    print_banner()
    logger = setup_logging("DEBUG")

    logger.info("Loading configuration...")
    config = load_config()

    # Create search agent
    agent = SearchAgent(config)

    # Test with BizBuySell only
    from utils import get_enabled_sites
    sites = get_enabled_sites(config)
    bizbuysell = [s for s in sites if "bizbuysell" in s["domain"].lower()][0]

    logger.info("Testing search with BizBuySell...")
    deals = agent.search_site(bizbuysell)

    logger.info(f"Found {len(deals)} deals from BizBuySell")

    for i, deal in enumerate(deals, 1):
        print(f"\n{i}. {deal['business_name']}")
        print(f"   Location: {deal['city']}, {deal['state']}")
        print(f"   Price: ${deal['asking_price']:,}")
        print(f"   Revenue: ${deal['revenue']:,}")
        print(f"   Cash Flow: ${deal['cash_flow']:,}")
        print(f"   Confidence: {deal['confidence_score']:.0%}")
        print(f"   URL: {deal['url']}")
