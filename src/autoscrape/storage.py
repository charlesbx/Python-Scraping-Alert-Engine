"""Storage functionality for persisting scraped data to CSV."""

import csv
import logging
import os
from typing import Any, Dict, List, Set

log = logging.getLogger("autoscrape.storage")


def load_existing_set(csv_path: str, unique_key: str) -> Set[str]:
    """
    Load existing unique values from a CSV file.

    Args:
        csv_path: Path to the CSV file
        unique_key: Column name to use as unique identifier

    Returns:
        Set of existing unique values
    """
    if not os.path.exists(csv_path) or os.stat(csv_path).st_size == 0:
        return set()

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or unique_key not in reader.fieldnames:
                log.warning(f"Unique key '{unique_key}' not found in {csv_path}")
                return set()
            return {row[unique_key] for row in reader if row.get(unique_key)}
    except Exception as e:
        log.error(f"Error loading existing data from {csv_path}: {e}")
        return set()


def append_csv(csv_path: str, rows: List[Dict[str, Any]]) -> None:
    """
    Append rows to a CSV file, creating it if it doesn't exist.

    Handles dynamic column management - if the file exists, uses existing columns,
    otherwise creates columns based on the data.

    Args:
        csv_path: Path to the CSV file
        rows: List of dictionaries to append
    """
    if not rows:
        return

    # Collect all field names from the rows
    fieldnames = sorted({k for r in rows for k in r.keys()})

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    file_exists = os.path.exists(csv_path) and os.stat(csv_path).st_size > 0

    # If file exists, use its existing fieldnames
    if file_exists:
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames:
                    fieldnames = reader.fieldnames
        except Exception as e:
            log.error(f"Error reading existing CSV headers from {csv_path}: {e}")

    # Append rows to the file
    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
        log.info(f"Appended {len(rows)} rows to {csv_path}")
    except Exception as e:
        log.error(f"Error writing to CSV {csv_path}: {e}")
        raise
