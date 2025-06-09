"""
学术研究MCP服务器模块

提供学术研究相关的MCP服务器实现，包括论文搜索、作者分析、
网络分析和趋势分析等功能。
"""

from .mcp_server import AcademicMCPServer

# 导出主要类
__all__ = [
    "AcademicMCPServer",
]

# 版本信息
__version__ = "1.0.0"

# 模块描述
__description__ = "Academic Research MCP Server - 学术研究MCP服务器"

# 支持的工具类型
SUPPORTED_TOOLS = [
    "search_papers",           # 搜索论文
    "get_paper_details",       # 获取论文详情
    "search_authors",          # 搜索作者
    "get_citation_network",    # 获取引用网络
    "get_collaboration_network", # 获取合作网络
    "get_research_trends",     # 获取研究趋势
    "analyze_research_landscape" # 分析研究领域
]

# 便捷函数：创建服务器实例
def create_server() -> AcademicMCPServer:
    """
    创建学术研究MCP服务器实例
    
    Returns:
        AcademicMCPServer: 配置好的服务器实例
    """
    return AcademicMCPServer()

# 便捷函数：获取支持的工具列表
def get_supported_tools() -> list[str]:
    """
    获取服务器支持的所有工具名称
    
    Returns:
        list[str]: 支持的工具名称列表
    """
    return SUPPORTED_TOOLS.copy()
