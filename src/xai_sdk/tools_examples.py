"""Example configurations for xAI tools.

This module provides pre-configured tool examples for common use cases,
making it easier for developers to get started with xAI agent tools.
"""

from xai_sdk.tools import web_search, x_search, code_execution


def create_research_tools():
    """Create a set of tools suitable for research agents.

    Returns:
        dict: A dictionary of tools configured for research tasks.
    """
    return {
        "web_search": web_search(enable_image_understanding=True),
        "code_execution": code_execution(),
        "x_search": x_search(enable_image_understanding=True),
    }


def create_development_tools():
    """Create a set of tools suitable for development and coding agents.

    Returns:
        dict: A dictionary of tools configured for development tasks.
    """
    return {
        "code_execution": code_execution(),
        "web_search": web_search(),
    }


def create_analytics_tools():
    """Create a set of tools suitable for data analytics agents.

    Returns:
        dict: A dictionary of tools configured for analytics tasks.
    """
    return {
        "code_execution": code_execution(),
        "web_search": web_search(enable_image_search=True),
    }
