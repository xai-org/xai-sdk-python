"""Pytest configuration and fixtures for the test suite."""
import pytest

def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    config.addinivalue_line("markers", "benchmark: mark test as a benchmark test")

def pytest_collection_modifyitems(items):
    """Modify test items to ensure benchmark tests are collected."""
    for item in items:
        if "benchmarks" in str(item.fspath):
            item.add_marker(pytest.mark.benchmark)
