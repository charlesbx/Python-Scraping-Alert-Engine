# AutoScrape Module

This directory contains the refactored, modular implementation of the AutoScrape engine.

## Architecture

The codebase is organized into focused modules with clear responsibilities:

### Core Modules

- **`scraper.py`** - Web scraping functionality
  - `fetch_html()` - HTTP requests with retry logic
  - `scrape_generic()` - Generic CSS selector-based scraping
  - Helper functions for field extraction and deduplication

- **`storage.py`** - Data persistence
  - `load_existing_set()` - Load unique identifiers from CSV
  - `append_csv()` - Append new rows to CSV files

- **`alerts.py`** - Notification systems
  - `send_alerts()` - Send alerts to Telegram and Discord
  - Message formatting and delivery functions

- **`cli.py`** - Command-line interface
  - Menu display and user interaction
  - Target selection and scraping workflows

- **`main.py`** - Application entry point
  - Configuration loading
  - Logging setup
  - Main application loop

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Type Safety**: Full type hints on all functions for better IDE support and documentation
3. **Error Handling**: Comprehensive error handling with proper logging
4. **Testability**: Pure functions and dependency injection for easy testing
5. **Documentation**: Comprehensive docstrings following Google style

## Usage

### As a Library

```python
from autoscrape.scraper import scrape_generic
from autoscrape.storage import append_csv

target = {
    'name': 'example',
    'url': 'https://example.com',
    'item': '.item',
    'fields': {
        'title': '.title::text',
        'link': '.link::attr(href)'
    }
}

items = scrape_generic(target)
append_csv('data/example.csv', items)
```

### As an Application

```python
from autoscrape.main import main

if __name__ == "__main__":
    main()
```

## Testing

All modules have corresponding test files in the `tests/` directory:
- `tests/test_scraper.py`
- `tests/test_storage.py`
- `tests/test_alerts.py`

Run tests with:
```bash
pytest tests/ -v
```

## Dependencies

- **requests** - HTTP client
- **beautifulsoup4** - HTML parsing
- **pyyaml** - Configuration loading
- **python-dotenv** - Environment variable management
