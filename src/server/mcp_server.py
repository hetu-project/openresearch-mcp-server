"""
学术研究MCP服务器核心实现
"""
import asyncio
from typing import Any, Sequence, Dict, Callable
import structlog
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest, CallToolResult,
    ListToolsRequest, ListToolsResult,
    TextContent, Tool
)

from src.config import settings
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
from src.mcp.tools.paper_tools import PaperTools   
from src.mcp.tools.author_tools import AuthorTools
from src.mcp.tools.network_tools import NetworkTools
from src.mcp.tools.trend_tools import TrendTools 

logger = structlog.get_logger()

class AcademicMCPServer:
    """学术研究MCP服务器 - 核心服务类"""
    
    def __init__(self):
        self.server = Server(settings.server_name)
        self.go_client: GoServiceClient = None
        self.data_processor: DataProcessor = None
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: list[Tool] = []
        
        # 注册MCP处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """注册MCP协议处理器"""
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
    
    async def initialize(self):
        """初始化服务器组件"""
        logger.info("Initializing Academic MCP Server components")
        
        try:
            # 初始化核心组件
            await self._initialize_core_components()
            
            # 初始化工具
            await self._initialize_tools()
            
            logger.info(
                "Academic MCP Server initialized successfully",
                tool_count=len(self.tools),
                available_tools=list(self.tools.keys())
            )
            
        except Exception as e:
            logger.error("Failed to initialize server", error=str(e))
            raise
    
    async def _initialize_core_components(self):
        """初始化核心组件"""
        # 初始化Go客户端
        self.go_client = GoServiceClient()
        
        # 初始化数据处理器
        self.data_processor = DataProcessor()
        
        logger.debug("Core components initialized")
    
    async def _initialize_tools(self):
        """初始化所有工具"""
        # 创建工具实例
        paper_tools = PaperTools(self.go_client, self.data_processor)
        author_tools = AuthorTools(self.go_client, self.data_processor)
        network_tools = NetworkTools(self.go_client, self.data_processor)
        trend_tools = TrendTools(self.go_client, self.data_processor)
        
        # 注册工具函数
        self.tools.update({
            # 论文相关工具
            "search_papers": paper_tools.search_papers,
            "get_paper_details": paper_tools.get_paper_details,
            
            # 作者相关工具
            "search_authors": author_tools.search_authors,
            "get_author_details": author_tools.get_author_details,
            
            # 网络分析工具
            "get_citation_network": network_tools.get_citation_network,
            "get_collaboration_network": network_tools.get_collaboration_network,
            
            # 趋势分析工具
            "get_research_trends": trend_tools.get_research_trends,
            "analyze_research_landscape": trend_tools.analyze_research_landscape
        })
        
        # 收集工具定义
        self.tool_definitions = []
        for tool_class in [paper_tools, author_tools, network_tools, trend_tools]:
            self.tool_definitions.extend(tool_class.get_tools())
        
        logger.debug("Tools initialized", tool_names=list(self.tools.keys()))
    
    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """列出可用工具"""
        logger.debug("Listing available tools", tool_count=len(self.tool_definitions))
        return ListToolsResult(tools=self.tool_definitions)
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """调用指定工具"""
        tool_name = request.params.name
        arguments = request.params.arguments or {}
        
        logger.info(
            "Executing tool",
            tool_name=tool_name,
            arguments=arguments
        )
        
        # 验证工具是否存在
        if tool_name not in self.tools:
            error_msg = f"Unknown tool: {tool_name}. Available tools: {list(self.tools.keys())}"
            logger.error("Tool not found", tool_name=tool_name)
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
        
        try:
            # 执行工具
            result = await self.tools[tool_name](arguments)
            
            logger.info(
                "Tool executed successfully",
                tool_name=tool_name,
                result_type=type(result).__name__
            )
            
            return CallToolResult(content=result, isError=False)
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(
                "Tool execution error",
                tool_name=tool_name,
                error=str(e),
                exc_info=True
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
    
    async def cleanup(self):
        """清理服务器资源"""
        logger.info("Starting server cleanup")
        
        try:
            if self.go_client:
                await self.go_client.__aexit__(None, None, None)
                logger.debug("Go client cleaned up")
            
            # 清理其他资源
            self.tools.clear()
            self.tool_definitions.clear()
            
            logger.info("Server cleanup completed successfully")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
            raise
