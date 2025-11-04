"""
AutoScrape - Web scraping and alert engine.

This is the entry point that uses the refactored modular code.
"""

import sys
import os

# Add src to path to import the refactored modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from autoscrape.main import main

if __name__ == "__main__":
    main()
