"""
MCP Module for OpenResearch

This module provides MCP (Model Context Protocol) tools for academic research.
"""

from .tools import (
    AuthorTools,
    NetworkTools,
    PaperTools,
    TrendTools,
    get_all_tools,
    create_tool_registry,
    get_all_tool_definitions,
    get_tool_categories,
    list_all_tools
)

__all__ = [
    "AuthorTools",
    "NetworkTools", 
    "PaperTools",
    "TrendTools",
    "get_all_tools",
    "create_tool_registry",
    "get_all_tool_definitions",
    "get_tool_categories",
    "list_all_tools"
]

__version__ = "1.0.0"
