"""
Utility functions for the M&A Deal Finder.
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import structlog
from colorama import Fore, Style, init

# Try to import Google Secret Manager (optional for local dev)
try:
    from google.cloud import secretmanager
    HAS_SECRET_MANAGER = True
except ImportError:
    HAS_SECRET_MANAGER = False

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def setup_logging(log_level: str = "INFO") -> structlog.BoundLogger:
    """
    Set up structured logging with color support.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    logger = structlog.get_logger()
    return logger


def get_secret(secret_name: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    Get a secret value from Google Secret Manager.

    Args:
        secret_name: Name of the secret
        project_id: Google Cloud project ID (uses GOOGLE_PROJECT_ID env if not provided)

    Returns:
        Secret value or None if not found
    """
    if not HAS_SECRET_MANAGER:
        return None

    try:
        # Get project ID
        if not project_id:
            project_id = os.getenv("GOOGLE_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")

        if not project_id:
            return None

        # Create client
        client = secretmanager.SecretManagerServiceClient()

        # Build secret name
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

        # Access secret
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")

        return secret_value

    except Exception as e:
        # Silently fail and return None - caller will use env var
        return None


def get_config_value(env_var: str, secret_name: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
    """
    Get configuration value from Secret Manager or environment variable.

    Priority:
    1. Google Secret Manager (if available)
    2. Environment variable
    3. Default value

    Args:
        env_var: Environment variable name
        secret_name: Secret Manager secret name (uses env_var if not provided)
        default: Default value if not found

    Returns:
        Configuration value
    """
    # Try Secret Manager first (production)
    if secret_name:
        secret_value = get_secret(secret_name)
        if secret_value:
            return secret_value

    # Fall back to environment variable (local development)
    env_value = os.getenv(env_var)
    if env_value:
        return env_value

    # Use default
    return default


def load_config() -> Dict[str, Any]:
    """
    Load configuration from .env file and YAML configs.

    Returns:
        Dictionary containing all configuration
    """
    # Load environment variables
    load_dotenv()

    # Get base directory (project root)
    base_dir = Path(__file__).parent.parent

    # Load YAML configs
    criteria_path = base_dir / "config" / "criteria.yaml"
    sites_path = base_dir / "config" / "sites.yaml"

    with open(criteria_path, "r") as f:
        criteria = yaml.safe_load(f)

    with open(sites_path, "r") as f:
        sites = yaml.safe_load(f)

    # Build complete config
    config = {
        # API Keys (try Secret Manager first, then .env)
        "anthropic_api_key": get_config_value("ANTHROPIC_API_KEY", "anthropic-api-key"),

        # Google Cloud
        "google_project_id": os.getenv("GOOGLE_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT"),
        "google_project_number": os.getenv("GOOGLE_PROJECT_NUMBER"),

        # Google Sheets
        "google_sheet_id": os.getenv("GOOGLE_SHEET_ID"),
        "google_sheet_name": os.getenv("GOOGLE_SHEET_NAME", "M&A Opportunities"),

        # Email
        "notification_email": os.getenv("NOTIFICATION_EMAIL"),

        # Search parameters
        "max_results_per_site": int(os.getenv("MAX_RESULTS_PER_SITE", "15")),
        "search_lookback_days": int(os.getenv("SEARCH_LOOKBACK_DAYS", "90")),
        "min_confidence_score": float(os.getenv("MIN_CONFIDENCE_SCORE", "0.65")),

        # Logging
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "enable_cloud_logging": os.getenv("ENABLE_CLOUD_LOGGING", "false").lower() == "true",

        # Development
        "dev_mode": os.getenv("DEV_MODE", "false").lower() == "true",
        "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",

        # Rate limiting
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "retry_delay_seconds": int(os.getenv("RETRY_DELAY_SECONDS", "2")),

        # Loaded configs
        "criteria": criteria,
        "sites": sites,
    }

    return config


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration and return list of errors.

    Args:
        config: Configuration dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Required fields
    required_fields = [
        ("anthropic_api_key", "ANTHROPIC_API_KEY"),
        ("google_project_id", "GOOGLE_PROJECT_ID"),
        ("google_sheet_id", "GOOGLE_SHEET_ID"),
        ("notification_email", "NOTIFICATION_EMAIL"),
    ]

    for field, env_var in required_fields:
        if not config.get(field):
            errors.append(f"Missing required environment variable: {env_var}")

    # Validate API key format
    if config.get("anthropic_api_key") and not config["anthropic_api_key"].startswith("sk-ant-"):
        errors.append("Invalid ANTHROPIC_API_KEY format (should start with 'sk-ant-')")

    return errors


def get_enabled_sites(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get list of enabled sites, sorted by priority.

    Args:
        config: Configuration dictionary

    Returns:
        List of enabled site configurations
    """
    sites_config = config.get("sites", {})

    # Combine priority and additional sites
    all_sites = sites_config.get("priority_sites", []) + sites_config.get("additional_sites", [])

    # Filter enabled sites
    enabled_sites = [site for site in all_sites if site.get("enabled", False)]

    # Sort by priority
    enabled_sites.sort(key=lambda x: x.get("priority", 999))

    return enabled_sites


def print_banner():
    """Print application banner."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{'  SoCal Business Group - AI-Powered M&A Deal Finder':^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_site_search_start(site_name: str, priority: int, total: int):
    """Print site search start message."""
    print(f"{Fore.YELLOW}🔍 Searching [{priority}/{total}]: {Fore.WHITE}{site_name}{Style.RESET_ALL}")


def print_site_search_complete(site_name: str, results_count: int):
    """Print site search complete message."""
    if results_count > 0:
        print(f"{Fore.GREEN}✓ Found {results_count} matches from {site_name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTBLACK_EX}○ No matches from {site_name}{Style.RESET_ALL}")


def print_summary(total_found: int, duration_seconds: float):
    """Print search summary."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.GREEN}✓ Search Complete{Style.RESET_ALL}")
    print(f"  Total opportunities found: {Fore.WHITE}{total_found}{Style.RESET_ALL}")
    print(f"  Duration: {Fore.WHITE}{duration_seconds:.1f}s{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def format_currency(amount: Optional[float]) -> str:
    """
    Format currency amount.

    Args:
        amount: Dollar amount

    Returns:
        Formatted string (e.g., "$1.2M", "$450K")
    """
    if amount is None or amount == 0:
        return "N/A"

    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    else:
        return f"${amount:,.0f}"


def deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate results by URL and business name.

    Args:
        results: List of deal dictionaries

    Returns:
        Deduplicated list
    """
    seen_urls = set()
    seen_names = set()
    unique_results = []

    for result in results:
        url = result.get("url", "").lower().strip()
        name = result.get("business_name", "").lower().strip()

        # Skip if we've seen this URL or exact business name
        if url and url in seen_urls:
            continue
        if name and name in seen_names:
            continue

        # Add to results
        unique_results.append(result)

        if url:
            seen_urls.add(url)
        if name:
            seen_names.add(name)

    return unique_results


def calculate_match_score(deal: Dict[str, Any], criteria: Dict[str, Any]) -> float:
    """
    Calculate match score for a deal (0.0 to 1.0).

    Args:
        deal: Deal dictionary
        criteria: Criteria configuration

    Returns:
        Match score (0.0 to 1.0)
    """
    weights = criteria.get("scoring_weights", {})
    score = 0.0

    # Revenue match
    revenue = deal.get("revenue", 0)
    revenue_min = criteria.get("revenue", {}).get("min", 0)
    revenue_max = criteria.get("revenue", {}).get("max", float("inf"))
    if revenue_min <= revenue <= revenue_max:
        score += weights.get("revenue_match", 0.15)

    # Cash flow match
    cash_flow = deal.get("cash_flow", 0)
    cash_flow_min = criteria.get("cash_flow", {}).get("min", 0)
    if cash_flow >= cash_flow_min:
        score += weights.get("cash_flow_match", 0.20)

    # Location match
    state = deal.get("state", "").upper()
    target_states = criteria.get("target_states", [])
    if state in target_states:
        score += weights.get("location_match", 0.15)

    # Use AI-provided confidence if available
    ai_confidence = deal.get("confidence_score", 0.5)
    score += ai_confidence * 0.5  # Weight AI assessment heavily

    return min(score, 1.0)  # Cap at 1.0


if __name__ == "__main__":
    # Test configuration loading
    print_banner()

    logger = setup_logging()
    logger.info("Loading configuration...")

    try:
        config = load_config()
        errors = validate_config(config)

        if errors:
            logger.error("Configuration errors", errors=errors)
        else:
            logger.info("Configuration loaded successfully")

            enabled_sites = get_enabled_sites(config)
            logger.info(f"Enabled sites: {len(enabled_sites)}")

            for site in enabled_sites:
                print(f"  - {site['name']} ({site['domain']})")

    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
