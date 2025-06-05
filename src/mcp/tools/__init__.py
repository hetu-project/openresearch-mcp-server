# src/mcp/tools/__init__.py
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
    "create_tool_registry",
    "get_all_tool_definitions",
    "get_tool_categories",
    "list_all_tools"
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
    registry["get_author_papers"] = author_tools.get_author_papers
    
    # Register paper tools
    paper_tools = tools["paper"]
    registry["search_papers"] = paper_tools.search_papers
    registry["get_paper_details"] = paper_tools.get_paper_details
    registry["get_paper_citations"] = paper_tools.get_paper_citations
    
    # Register network tools
    network_tools = tools["network"]
    registry["get_citation_network"] = network_tools.get_citation_network
    registry["get_collaboration_network"] = network_tools.get_collaboration_network
    
    # Register trend tools
    trend_tools = tools["trend"]
    registry["get_trending_papers"] = trend_tools.get_trending_papers
    registry["get_top_keywords"] = trend_tools.get_top_keywords
    
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

# 工具分类定义 - MVP版本
TOOL_CATEGORIES = {
    "author": {
        "name": "Author Tools",
        "description": "Tools for searching and analyzing academic authors",
        "tools": ["search_authors", "get_author_details", "get_author_papers"]
    },
    "paper": {
        "name": "Paper Tools", 
        "description": "Tools for searching and analyzing academic papers",
        "tools": ["search_papers", "get_paper_details", "get_paper_citations"]
    },
    "network": {
        "name": "Network Analysis Tools",
        "description": "Tools for analyzing citation and collaboration networks",
        "tools": ["get_citation_network", "get_collaboration_network"]
    },
    "trend": {
        "name": "Trend Analysis Tools",
        "description": "Tools for analyzing research trends and hot topics",
        "tools": ["get_trending_papers", "get_top_keywords"]
    }
}

def get_tool_categories():
    """
    Get information about tool categories.
    
    Returns:
        dict: Tool categories with descriptions
    """
    return TOOL_CATEGORIES

def list_all_tools():
    """
    List all available tools with their descriptions.
    
    Returns:
        dict: Dictionary with tool information organized by category
    """
    # 工具描述定义
    tool_descriptions = {
        # Author tools
        "search_authors": "Search for academic authors by name, affiliation, or research area",
        "get_author_details": "Get detailed information about specific authors including metrics and collaborations",
        "get_author_papers": "Get all papers published by a specific author",
        
        # Paper tools
        "search_papers": "Search for academic papers by keywords, authors, year, venue, or other criteria",
        "get_paper_details": "Get detailed information about specific papers including abstract and metadata",
        "get_paper_citations": "Get citation relationships for a specific paper (citing and cited papers)",
        
        # Network tools
        "get_citation_network": "Generate citation network graph showing paper relationships",
        "get_collaboration_network": "Generate collaboration network graph showing author relationships",
        
        # Trend tools
        "get_trending_papers": "Get currently trending/popular papers in specified time window",
        "get_top_keywords": "Get currently popular research keywords/topics with paper counts"
    }
    
    result = {}
    
    for category, info in TOOL_CATEGORIES.items():
        result[category] = {
            "category_name": info["name"],
            "category_description": info["description"],
            "tools": []
        }
        
        for tool_name in info["tools"]:
            result[category]["tools"].append({
                "name": tool_name,
                "description": tool_descriptions.get(tool_name, "No description available")
            })
    
    return result

def get_tool_stats():
    """
    Get basic statistics about available tools.
    
    Returns:
        dict: Tool statistics
    """
    total_tools = sum(len(cat["tools"]) for cat in TOOL_CATEGORIES.values())
    
    return {
        "total_tools": total_tools,
        "total_categories": len(TOOL_CATEGORIES),
        "tools_by_category": {
            cat: len(info["tools"]) 
            for cat, info in TOOL_CATEGORIES.items()
        }
    }

def validate_tool_registry(go_client, data_processor):
    """
    Validate that all tools in categories are properly registered.
    
    Args:
        go_client: GoServiceClient instance
        data_processor: DataProcessor instance
        
    Returns:
        dict: Validation results
    """
    registry = create_tool_registry(go_client, data_processor)
    
    # 收集所有分类中的工具
    all_category_tools = []
    for category_info in TOOL_CATEGORIES.values():
        all_category_tools.extend(category_info["tools"])
    
    # 检查缺失的工具
    missing_tools = [
        tool for tool in all_category_tools 
        if tool not in registry
    ]
    
    # 检查多余的工具
    extra_tools = [
        tool for tool in registry.keys() 
        if tool not in all_category_tools
    ]
    
    return {
        "valid": len(missing_tools) == 0 and len(extra_tools) == 0,
        "total_registered": len(registry),
        "total_categorized": len(all_category_tools),
        "missing_tools": missing_tools,
        "extra_tools": extra_tools
    }

def get_tool_by_name(tool_name: str, go_client, data_processor):
    """
    Get a specific tool handler by name.
    
    Args:
        tool_name: Name of the tool
        go_client: GoServiceClient instance
        data_processor: DataProcessor instance
        
    Returns:
        Tool handler function or None if not found
    """
    registry = create_tool_registry(go_client, data_processor)
    return registry.get(tool_name)

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
