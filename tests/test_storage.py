"""Tests for storage module."""

import csv
import os
import sys
import tempfile

import pytest

# Add src to path for direct test execution (alternative: pip install -e .)
if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "src")):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from autoscrape.storage import append_csv, load_existing_set


class TestLoadExistingSet:
    """Tests for load_existing_set function."""

    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file returns empty set."""
        import tempfile

        nonexistent_path = os.path.join(tempfile.gettempdir(), "nonexistent_test_file.csv")
        result = load_existing_set(nonexistent_path, "link")
        assert result == set()

    def test_load_from_valid_csv(self):
        """Test loading from valid CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["link", "title"])
            writer.writeheader()
            writer.writerow({"link": "url1", "title": "Title 1"})
            writer.writerow({"link": "url2", "title": "Title 2"})
            f.flush()
            temp_path = f.name

        try:
            result = load_existing_set(temp_path, "link")
            assert result == {"url1", "url2"}
        finally:
            os.unlink(temp_path)

    def test_load_missing_unique_key(self):
        """Test loading when unique key doesn't exist in CSV."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["title", "author"])
            writer.writeheader()
            writer.writerow({"title": "Title 1", "author": "Author 1"})
            f.flush()
            temp_path = f.name

        try:
            result = load_existing_set(temp_path, "link")
            assert result == set()
        finally:
            os.unlink(temp_path)


class TestAppendCsv:
    """Tests for append_csv function."""

    def test_append_to_new_file(self):
        """Test appending to a new file creates it with headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            rows = [{"link": "url1", "title": "Title 1"}, {"link": "url2", "title": "Title 2"}]

            append_csv(csv_path, rows)

            assert os.path.exists(csv_path)
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = list(reader)
                assert len(data) == 2
                assert data[0]["link"] == "url1"

    def test_append_to_existing_file(self):
        """Test appending to existing file preserves existing data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")

            # Create initial file
            initial_rows = [{"link": "url1", "title": "Title 1"}]
            append_csv(csv_path, initial_rows)

            # Append new rows
            new_rows = [{"link": "url2", "title": "Title 2"}]
            append_csv(csv_path, new_rows)

            # Verify both rows exist
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = list(reader)
                assert len(data) == 2
                assert data[0]["link"] == "url1"
                assert data[1]["link"] == "url2"

    def test_append_empty_list(self):
        """Test appending empty list does nothing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")

            append_csv(csv_path, [])

            assert not os.path.exists(csv_path)
