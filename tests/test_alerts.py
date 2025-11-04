"""Tests for alerts module."""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src to path for direct test execution (alternative: pip install -e .)
if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "src")):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from autoscrape.alerts import _format_alert_message, send_alerts


class TestFormatAlertMessage:
    """Tests for _format_alert_message function."""

    def test_format_with_title(self):
        """Test formatting alert message with title field."""
        items = [{"link": "url1", "title": "Title 1"}, {"link": "url2", "title": "Title 2"}]

        result = _format_alert_message(items, "link", "test_source")

        assert "2 new item(s) detected for test_source" in result
        assert "url1" in result
        assert "Title 1" in result

    def test_format_with_limit(self):
        """Test that formatting limits to 10 items."""
        items = [{"link": f"url{i}", "title": f"Title {i}"} for i in range(15)]

        result = _format_alert_message(items, "link", "test_source")

        assert "15 new item(s)" in result
        lines = result.split("\n")
        # 1 header line + 10 item lines
        assert len(lines) == 11


class TestSendAlerts:
    """Tests for send_alerts function."""

    @patch("autoscrape.alerts.requests.post")
    @patch.dict(
        os.environ, {"TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "test_chat_id"}
    )
    def test_send_telegram_alert(self, mock_post):
        """Test sending Telegram alert."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        items = [{"link": "url1", "title": "Title 1"}]
        send_alerts(items, "link", "test_source")

        # Should call Telegram API
        assert any("telegram.org" in str(call) for call in mock_post.call_args_list)

    @patch("autoscrape.alerts.requests.post")
    @patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test"})
    def test_send_discord_alert(self, mock_post):
        """Test sending Discord alert."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        items = [{"link": "url1", "title": "Title 1"}]
        send_alerts(items, "link", "test_source")

        # Should call Discord webhook
        assert any("discord.com" in str(call) for call in mock_post.call_args_list)

    @patch("autoscrape.alerts.requests.post")
    def test_send_alerts_empty_items(self, mock_post):
        """Test that empty items list doesn't send alerts."""
        send_alerts([], "link", "test_source")

        mock_post.assert_not_called()

    @patch("autoscrape.alerts.requests.post")
    @patch.dict(os.environ, {}, clear=True)
    def test_send_alerts_no_credentials(self, mock_post):
        """Test that missing credentials doesn't crash."""
        items = [{"link": "url1", "title": "Title 1"}]

        # Should not raise exception
        send_alerts(items, "link", "test_source")

        mock_post.assert_not_called()
