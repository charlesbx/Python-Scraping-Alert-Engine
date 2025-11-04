"""Alert notification functionality for Telegram and Discord."""

import logging
import os
from typing import Any, Dict, List

import requests

log = logging.getLogger("autoscrape.alerts")


def send_alerts(new_items: List[Dict[str, Any]], unique_key: str, source_name: str) -> None:
    """
    Send alerts to configured channels (Telegram and/or Discord).

    Args:
        new_items: List of new items detected
        unique_key: Key to use for identifying items in alert message
        source_name: Name of the scraping source
    """
    if not new_items:
        return

    message = _format_alert_message(new_items, unique_key, source_name)

    # Send to Telegram
    _send_telegram_alert(message)

    # Send to Discord
    _send_discord_alert(message)


def _format_alert_message(items: List[Dict[str, Any]], unique_key: str, source_name: str) -> str:
    """
    Format alert message for new items.

    Args:
        items: List of items to include in alert
        unique_key: Key to identify items
        source_name: Name of the source

    Returns:
        Formatted alert message
    """
    lines = [f"🔔 {len(items)} new item(s) detected for {source_name}:"]
    preview = items[:10]  # Limit to first 10 items

    for item in preview:
        parts = []

        # Add unique key value
        if item.get(unique_key):
            parts.append(str(item.get(unique_key)))

        # Add first available descriptive field
        for key in ("title", "company", "price", "posted"):
            if key in item and item.get(key):
                parts.append(str(item[key]))
                break

        lines.append("• " + " — ".join(parts))

    return "\n".join(lines)


def _send_telegram_alert(message: str) -> None:
    """
    Send alert message to Telegram.

    Args:
        message: Message to send
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        log.debug("Telegram credentials not configured, skipping")
        return

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
            timeout=15,
        )
        response.raise_for_status()
        log.info("Telegram alert sent successfully")
    except Exception as e:
        log.error(f"Failed to send Telegram alert: {e}")


def _send_discord_alert(message: str) -> None:
    """
    Send alert message to Discord webhook.

    Args:
        message: Message to send
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        log.debug("Discord webhook not configured, skipping")
        return

    try:
        response = requests.post(webhook_url, json={"content": message}, timeout=15)
        response.raise_for_status()
        log.info("Discord alert sent successfully")
    except Exception as e:
        log.error(f"Failed to send Discord alert: {e}")
