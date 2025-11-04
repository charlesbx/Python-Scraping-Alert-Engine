"""Tests for scraper module."""

import os
import sys
from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from autoscrape.scraper import _deduplicate_items, _extract_field, fetch_html, scrape_generic


class TestFetchHtml:
    """Tests for fetch_html function."""

    @patch("autoscrape.scraper.requests.get")
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetch."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_html("https://example.com")

        assert result == "<html><body>Test</body></html>"
        mock_get.assert_called_once()

    @patch("autoscrape.scraper.requests.get")
    @patch("autoscrape.scraper.time.sleep")
    def test_fetch_html_retry(self, mock_sleep, mock_get):
        """Test retry logic on failure."""
        from requests.exceptions import RequestException

        # First two calls fail, third succeeds
        mock_response = Mock()
        mock_response.text = "<html>Success</html>"
        mock_response.raise_for_status = Mock()

        mock_get.side_effect = [
            RequestException("Error 1"),
            RequestException("Error 2"),
            mock_response,
        ]

        result = fetch_html("https://example.com")

        assert result == "<html>Success</html>"
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2


class TestExtractField:
    """Tests for _extract_field function."""

    def test_extract_text(self):
        """Test extracting text content."""
        html = '<div><span class="title">Test Title</span></div>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        result = _extract_field(element, ".title::text", "title", "https://example.com")

        assert result == "Test Title"

    def test_extract_attribute(self):
        """Test extracting attribute value."""
        html = '<div><a class="link" href="/path">Link</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        result = _extract_field(element, ".link::attr(href)", "link", "https://example.com")

        assert result == "https://example.com/path"

    def test_extract_missing_element(self):
        """Test extracting from non-existent element."""
        html = "<div><span>Test</span></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        result = _extract_field(element, ".notfound::text", "field", "https://example.com")

        assert result is None


class TestDeduplicateItems:
    """Tests for _deduplicate_items function."""

    def test_deduplicate_identical_items(self):
        """Test removing duplicate items."""
        items = [
            {"title": "Item 1", "link": "url1"},
            {"title": "Item 2", "link": "url2"},
            {"title": "Item 1", "link": "url1"},  # duplicate
        ]

        result = _deduplicate_items(items)

        assert len(result) == 2
        assert {"title": "Item 1", "link": "url1"} in result
        assert {"title": "Item 2", "link": "url2"} in result

    def test_deduplicate_unique_items(self):
        """Test items that are already unique."""
        items = [
            {"title": "Item 1", "link": "url1"},
            {"title": "Item 2", "link": "url2"},
        ]

        result = _deduplicate_items(items)

        assert len(result) == 2


class TestScrapeGeneric:
    """Tests for scrape_generic function."""

    @patch("autoscrape.scraper.fetch_html")
    def test_scrape_generic(self, mock_fetch):
        """Test generic scraping with mock HTML."""
        mock_html = """
        <html>
            <body>
                <div class="item">
                    <a class="title" href="/item1">Item 1</a>
                </div>
                <div class="item">
                    <a class="title" href="/item2">Item 2</a>
                </div>
            </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        target = {
            "name": "test_site",
            "url": "https://example.com",
            "item": ".item",
            "fields": {"title": ".title::text", "link": ".title::attr(href)"},
        }

        result = scrape_generic(target)

        assert len(result) == 2
        assert result[0]["source"] == "test_site"
        assert result[0]["title"] == "Item 1"
        assert result[0]["link"] == "https://example.com/item1"
