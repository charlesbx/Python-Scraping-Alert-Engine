"""Web scraping functionality for AutoScrape."""

import logging
import random
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

log = logging.getLogger("autoscrape.scraper")


def fetch_html(url: str, max_retries: int = 3, base_delay: float = 1.0, timeout: int = 15) -> str:
    """
    Fetch HTML content from a URL with exponential backoff retry logic.

    Args:
        url: The URL to fetch
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        RequestException: If all retry attempts fail
    """
    user_agent = "Mozilla/5.0 (compatible; AutoScrapeAlerts/1.0; +https://example.com)"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
            response.raise_for_status()
            return response.text
        except RequestException as e:
            if attempt == max_retries:
                log.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                raise

            sleep_duration = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            log.warning(f"Retry {attempt}/{max_retries} for {url}: {e}")
            time.sleep(sleep_duration)

    # This should never be reached due to the raise in the loop
    raise RequestException(f"Failed to fetch {url}")


def scrape_generic(target: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generic web scraper that extracts data based on CSS selectors.

    Args:
        target: Configuration dictionary containing:
            - url: Target URL to scrape
            - item: CSS selector for items
            - fields: Dictionary mapping field names to CSS selectors
            - name: Name of the scraping target

    Returns:
        List of dictionaries containing scraped data
    """
    url = target["url"]
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    items = []
    for element in soup.select(target["item"]):
        row = {}
        for field, selector in target["fields"].items():
            value = _extract_field(element, selector, field, url)
            row[field] = value

        if any(v for v in row.values()):
            row["source"] = target.get("name")
            items.append(row)

    # Deduplicate items
    return _deduplicate_items(items)


def _extract_field(
    element: BeautifulSoup, selector: str, field: str, base_url: str
) -> Optional[str]:
    """
    Extract a field value from an HTML element using a CSS selector.

    Args:
        element: BeautifulSoup element to extract from
        selector: CSS selector with optional ::attr() or ::text suffix
        field: Field name (used to determine if URL conversion is needed)
        base_url: Base URL for converting relative URLs to absolute

    Returns:
        Extracted value or None if not found
    """
    if "::attr(" in selector:
        css, rest = selector.split("::attr(", 1)
        attr = rest.rstrip(")")
        node = element.select_one(css.strip())
        value = node.get(attr) if node else None

        # Convert relative URLs to absolute for link/url fields
        if field.lower() in ("link", "url") and value:
            value = urljoin(base_url, value)
        return value

    elif selector.endswith("::text"):
        css = selector[:-6].strip()
        node = element.select_one(css)
        return node.get_text(strip=True) if node else None

    else:
        node = element.select_one(selector)
        return node.get_text(strip=True) if node else None


def _deduplicate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate items from a list based on all field values.

    Args:
        items: List of dictionaries to deduplicate

    Returns:
        Deduplicated list of items
    """
    seen_rows = set()
    deduped = []

    for row in items:
        key_tuple = tuple(sorted((k, row.get(k)) for k in row.keys()))
        if key_tuple not in seen_rows:
            seen_rows.add(key_tuple)
            deduped.append(row)

    return deduped
