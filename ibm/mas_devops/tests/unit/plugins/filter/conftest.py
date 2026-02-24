"""
Pytest configuration and fixtures for filter plugin tests.
"""
import sys
from pathlib import Path

import pytest


# Add the plugins/filter directory to the Python path so we can import filters
filter_plugin_path = Path(__file__).parent.parent.parent.parent.parent / "plugins" / "filter"
sys.path.insert(0, str(filter_plugin_path))

# Made with Bob
