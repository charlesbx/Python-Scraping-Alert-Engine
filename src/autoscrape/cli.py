"""Command-line interface for AutoScrape."""

import logging
from typing import Any, Dict, List

from .alerts import send_alerts
from .scraper import scrape_generic
from .storage import append_csv, load_existing_set

log = logging.getLogger("autoscrape.cli")


def display_menu(alerts_enabled: bool) -> str:
    """
    Display the interactive CLI menu and get user choice.

    Args:
        alerts_enabled: Whether alerts are currently enabled

    Returns:
        User's menu choice
    """
    print("\n=== AutoScrape Alerts ===")
    print("[1] Scrape all sites")
    print("[2] Choose a specific site to scrape")
    print("[3] Dry-run mode (test without saving)")
    print("[4] Scrape with item limit")
    print("[o] Alert options: " + ("Enabled 🔔" if alerts_enabled else "Disabled 🔕"))
    print("[q] Quit")
    choice = input("→ Choice: ").strip()
    return choice


def scrape_target(
    target: Dict[str, Any],
    unique_key: str,
    csv_path: str,
    alerts_enabled: bool,
    dry_run: bool = False,
) -> None:
    """
    Scrape a single target and handle storage/alerts.

    Args:
        target: Target configuration dictionary
        unique_key: Key to use for deduplication
        csv_path: Default CSV path (can be overridden by target)
        alerts_enabled: Whether to send alerts for new items
        dry_run: If True, don't save data or send alerts
    """
    log.info(f"Scraping: {target['name']}")

    try:
        scraped = scrape_generic(target)
    except Exception as e:
        log.error(f"Failed to scrape {target['name']}: {e}")
        return

    if dry_run:
        log.info(f"Dry-run: {len(scraped)} items scraped (not saved)")
        return

    target_csv = target.get("csv_path", csv_path)
    existing = load_existing_set(target_csv, unique_key)
    new_items = [row for row in scraped if row.get(unique_key) and row[unique_key] not in existing]

    if new_items:
        log.info(f"{len(new_items)} new item(s) for {target['name']}")
        append_csv(target_csv, new_items)

        if alerts_enabled:
            try:
                send_alerts(new_items, unique_key, target["name"])
            except Exception as e:
                log.error(f"Failed to send alerts: {e}")
    else:
        log.info(f"No new items for {target['name']}")


def scrape_all_targets(
    targets: List[Dict[str, Any]], unique_key: str, csv_path: str, alerts_enabled: bool
) -> None:
    """
    Scrape all configured targets.

    Args:
        targets: List of target configurations
        unique_key: Key to use for deduplication
        csv_path: Default CSV path
        alerts_enabled: Whether to send alerts
    """
    for target in targets:
        scrape_target(target, unique_key, csv_path, alerts_enabled)


def choose_and_scrape_target(
    targets: List[Dict[str, Any]], unique_key: str, csv_path: str, alerts_enabled: bool
) -> None:
    """
    Display target list and scrape the selected one.

    Args:
        targets: List of target configurations
        unique_key: Key to use for deduplication
        csv_path: Default CSV path
        alerts_enabled: Whether to send alerts
    """
    print("\nAvailable sites:")
    for i, target in enumerate(targets, start=1):
        print(f"[{i}] {target['name']}")

    try:
        idx = int(input("→ Choose a site: ")) - 1
        if 0 <= idx < len(targets):
            target = targets[idx]
            scrape_target(target, unique_key, csv_path, alerts_enabled)
        else:
            print("❌ Invalid site number")
    except (ValueError, IndexError):
        print("❌ Invalid input")


def dry_run_scrape(targets: List[Dict[str, Any]]) -> None:
    """
    Run a dry-run scrape showing preview without saving.

    Args:
        targets: List of target configurations
    """
    print("Dry-run mode: nothing is saved or sent.")
    if targets:
        target = targets[0]
        try:
            scraped = scrape_generic(target)
            print(f"Preview (first 5 items):")
            for item in scraped[:5]:
                print(f"  {item}")
        except Exception as e:
            log.error(f"Dry-run failed: {e}")


def scrape_with_limit(targets: List[Dict[str, Any]], unique_key: str) -> None:
    """
    Scrape with a limit on number of items.

    Args:
        targets: List of target configurations
        unique_key: Key to display in preview
    """
    try:
        limit = int(input("Item limit: "))
        for target in targets:
            print(f"🔍 Scraping: {target['name']}")
            scraped = scrape_generic(target)[:limit]
            print(f"Preview ({limit} items):")
            for item in scraped:
                title = item.get("title") or ""
                key_value = item.get(unique_key) or ""
                print(f"• {key_value} {title}".strip())
    except ValueError:
        print("❌ Invalid number")
    except Exception as e:
        log.error(f"Failed to scrape with limit: {e}")
