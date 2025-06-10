"""
学术研究MCP服务器核心实现 - 修正版本
"""
import asyncio
from typing import Any, Optional, Sequence, Dict, Callable
import structlog
from mcp.server import Server
from mcp.types import (
    TextContent, Tool
)

from src.config import settings
from src.clients.go_client import GoServiceClient
from src.services.data_processor import DataProcessor
from src.core.tools import create_tool_registry, get_all_tool_definitions

logger = structlog.get_logger()

class AcademicMCPServer:
    """学术研究MCP服务器 - 修正版本"""
    
    def __init__(self):
        self.server = Server(settings.server_name)
        self.go_client: Optional[GoServiceClient] = None
        self.data_processor: Optional[DataProcessor] = None
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: list[Tool] = []
        
        # 注册 MCP 处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """使用 MCP 装饰器注册处理器"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """列出可用工具"""
            logger.debug("Listing available tools", tool_count=len(self.tool_definitions))
            return self.tool_definitions
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None = None) -> list[TextContent]:
            """调用指定工具"""
            arguments = arguments or {}
            
            logger.info(
                "Executing tool",
                tool_name=name,
                arguments=arguments
            )
            
            # 验证工具是否存在
            if name not in self.tools:
                error_msg = f"Unknown tool: {name}. Available tools: {list(self.tools.keys())}"
                logger.error("Tool not found", tool_name=name)
                raise ValueError(error_msg)
            
            try:
                # 执行工具
                result = await self.tools[name](arguments)
                
                logger.info(
                    "Tool executed successfully",
                    tool_name=name,
                    result_type=type(result).__name__,
                    result_count=len(result) if isinstance(result, list) else 1
                )
                
                # 确保返回的是 TextContent 列表
                if isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
                    return result
                elif isinstance(result, list):
                    # 如果是其他类型的列表，转换为 TextContent
                    return [TextContent(type="text", text=str(item)) for item in result]
                else:
                    # 如果是单个值，转换为 TextContent 列表
                    return [TextContent(type="text", text=str(result))]
                
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.debug("Tool_arguments: ", tool_arguments=arguments)
                logger.error(
                    "Tool execution error",
                    tool_name=name,
                    error=str(e),
                    exc_info=True
                )
                raise RuntimeError(error_msg)
    
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
        # 注意：不在这里调用 connect()，因为会在 async with 中自动连接
        
        # 初始化数据处理器
        self.data_processor = DataProcessor()
        
        logger.debug("Core components initialized")
    
    async def _initialize_tools(self):
        """初始化所有工具"""
        assert self.go_client is not None, "GoServiceClient must be initialized before tools"
        assert self.data_processor is not None, "DataProcessor must be initialized before tools"

        try:
            # 使用统一的工具注册表
            self.tools = create_tool_registry(self.go_client, self.data_processor)
            
            # 获取所有工具定义
            self.tool_definitions = get_all_tool_definitions(self.go_client, self.data_processor)
            
            logger.info(
                "Tools initialized successfully",
                tool_count=len(self.tools),
                definition_count=len(self.tool_definitions),
                tool_names=list(self.tools.keys())
            )
            
        except Exception as e:
            logger.error("Failed to initialize tools", error=str(e))
            raise
    
    async def cleanup(self):
        """清理服务器资源"""
        logger.info("Starting server cleanup")
        
        try:
            # 清理Go客户端 - 不需要手动断开，async with 会处理
            self.go_client = None
            
            # 清理工具注册表
            self.tools.clear()
            self.tool_definitions.clear()
            
            # 清理数据处理器
            self.data_processor = None
            
            logger.info("Server cleanup completed successfully")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
            raise
