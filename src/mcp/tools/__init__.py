"""
MCP Tools Module

This module contains all the tool implementations for the OpenResearch MCP server.
Each tool class provides specific functionality for academic research data analysis.
"""

from .author_tools import AuthorTools
from .network_tools import NetworkTools
from .paper_tools import PaperTools
from .trend_tools import TrendTools

# Export all tool classes
__all__ = [
    "AuthorTools",
    "NetworkTools", 
    "PaperTools",
    "TrendTools",
    "get_all_tools",
    "create_tool_registry"
]

def get_all_tools(go_client, data_processor):
    """
    Create instances of all tool classes with the provided dependencies.
    
    Args:
        go_client: GoServiceClient instance for backend communication
        data_processor: DataProcessor instance for data processing
        
    Returns:
        dict: Dictionary mapping tool names to tool instances
    """
    return {
        "author": AuthorTools(go_client, data_processor),
        "network": NetworkTools(go_client, data_processor),
        "paper": PaperTools(go_client, data_processor),
        "trend": TrendTools(go_client, data_processor)
    }

def create_tool_registry(go_client, data_processor):
    """
    Create a comprehensive tool registry with all available tools.
    
    Args:
        go_client: GoServiceClient instance
        data_processor: DataProcessor instance
        
    Returns:
        dict: Dictionary mapping individual tool names to their handler functions
    """
    tools = get_all_tools(go_client, data_processor)
    
    registry = {}
    
    # Register author tools
    author_tools = tools["author"]
    registry["search_authors"] = author_tools.search_authors
    registry["get_author_details"] = author_tools.get_author_details
    
    # Register network tools
    network_tools = tools["network"]
    registry["get_citation_network"] = network_tools.get_citation_network
    registry["get_collaboration_network"] = network_tools.get_collaboration_network
    
    # Register paper tools
    paper_tools = tools["paper"]
    registry["search_papers"] = paper_tools.search_papers
    registry["get_paper_details"] = paper_tools.get_paper_details
    
    # Register trend tools
    trend_tools = tools["trend"]
    registry["get_research_trends"] = trend_tools.get_research_trends
    registry["analyze_research_landscape"] = trend_tools.analyze_research_landscape
    
    return registry

def get_all_tool_definitions(go_client, data_processor):
    """
    Get all tool definitions from all tool classes.
    
    Args:
        go_client: GoServiceClient instance
        data_processor: DataProcessor instance
        
    Returns:
        list: List of all Tool definitions
    """
    tools = get_all_tools(go_client, data_processor)
    
    all_definitions = []
    for tool_instance in tools.values():
        all_definitions.extend(tool_instance.get_tools())
    
    return all_definitions

# Tool categories for organization
TOOL_CATEGORIES = {
    "author": {
        "name": "Author Tools",
        "description": "Tools for searching and analyzing academic authors",
        "tools": ["search_authors", "get_author_details"]
    },
    "paper": {
        "name": "Paper Tools", 
        "description": "Tools for searching and analyzing academic papers",
        "tools": ["search_papers", "get_paper_details"]
    },
    "network": {
        "name": "Network Analysis Tools",
        "description": "Tools for analyzing citation and collaboration networks",
        "tools": ["get_citation_network", "get_collaboration_network"]
    },
    "trend": {
        "name": "Trend Analysis Tools",
        "description": "Tools for analyzing research trends and landscapes",
        "tools": ["get_research_trends", "analyze_research_landscape"]
    }
}

def get_tool_categories():
    """
    Get information about tool categories.
    
    Returns:
        dict: Tool categories with descriptions
    """
    return TOOL_CATEGORIES

def get_tools_by_category(category: str, go_client, data_processor):
    """
    Get tools for a specific category.
    
    Args:
        category: Category name ("author", "paper", "network", "trend")
        go_client: GoServiceClient instance
        data_processor: DataProcessor instance
        
    Returns:
        Tool instance for the specified category or None if not found
    """
    tools = get_all_tools(go_client, data_processor)
    return tools.get(category)
