"""
Academic Research MCP Server Module

Provides academic research related MCP server implementation, including paper search,
author analysis, network analysis and trend analysis functions.
"""

from .mcp_server import AcademicMCPServer

__all__ = [
    "AcademicMCPServer",
]

__version__ = "1.0.0"

__description__ = "Academic Research MCP Server"

SUPPORTED_TOOLS = [
    "search_papers",           # Search papers
    "get_paper_details",       # Get paper details
    "search_authors",          # Search authors
    "get_citation_network",    # Get citation network
    "get_collaboration_network", # Get collaboration network
    "get_research_trends",     # Get research trends
    "analyze_research_landscape" # Analyze research landscape
]

def create_server() -> AcademicMCPServer:
    """
    Create an academic research MCP server instance
    
    Returns:
        AcademicMCPServer: Configured server instance
    """
    return AcademicMCPServer()

def get_supported_tools() -> list[str]:
    """
    Get all tool names supported by the server
    
    Returns:
        list[str]: List of supported tool names
    """
    return SUPPORTED_TOOLS.copy()