"""Main entry point for AutoScrape application."""

import logging
import os
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from .cli import (
    choose_and_scrape_target,
    display_menu,
    dry_run_scrape,
    scrape_all_targets,
    scrape_with_limit,
)

# Load environment variables
load_dotenv()


def setup_logging() -> None:
    """Configure logging for the application."""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler("logs/app.log", encoding="utf-8"), logging.StreamHandler()],
    )


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    """Main application loop."""
    setup_logging()
    log = logging.getLogger("autoscrape.main")

    try:
        config = load_config()
    except Exception as e:
        log.error(f"Failed to load configuration: {e}")
        return

    csv_path = config["storage"]["csv_path"]
    unique_key = config["storage"].get("unique_key", "link")
    alerts_enabled = config["alerts"].get("enabled", False)
    targets = config.get("targets", [])

    if not targets:
        log.error("No targets configured in config.yaml")
        return

    while True:
        choice = display_menu(alerts_enabled)

        if choice == "o":
            print("\n=== Alert Options ===")
            alerts_enabled = not alerts_enabled
            config["alerts"]["enabled"] = alerts_enabled
            status = "enabled 🔔" if alerts_enabled else "disabled 🔕"
            print(f"Alerts {status}")
            log.info(f"Alerts {status}")
            continue

        elif choice == "1":
            scrape_all_targets(targets, unique_key, csv_path, alerts_enabled)

        elif choice == "2":
            choose_and_scrape_target(targets, unique_key, csv_path, alerts_enabled)

        elif choice == "3":
            dry_run_scrape(targets)

        elif choice == "4":
            scrape_with_limit(targets, unique_key)

        elif choice.lower() == "q":
            print("👋 Bye")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
