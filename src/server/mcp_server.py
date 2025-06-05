"""
学术研究MCP服务器核心实现 - MVP版本
"""
import asyncio
from typing import Any, Optional, Sequence, Dict, Callable
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
from src.core.tools import create_tool_registry, get_all_tool_definitions

logger = structlog.get_logger()

class AcademicMCPServer:
    """学术研究MCP服务器 - MVP版本"""
    
    def __init__(self):
        self.server = Server(settings.server_name)
        self.go_client: Optional[GoServiceClient] = None
        self.data_processor: Optional[DataProcessor] = None
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: list[Tool] = []
        
        # 注册MCP处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """注册MCP协议处理器"""
        setattr(self.server, 'list_tools', self.list_tools)
        setattr(self.server, 'call_tool', self.call_tool)
    
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
        await self.go_client.connect()
        
        # 初始化数据处理器
        self.data_processor = DataProcessor()
        
        logger.debug("Core components initialized")
    
    async def _initialize_tools(self):
        """初始化所有工具 - 使用统一的工具注册表"""
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
                result_type=type(result).__name__,
                result_count=len(result) if isinstance(result, list) else 1
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
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查Go服务连接
            go_service_status = "unknown"
            if self.go_client:
                try:
                    await self.go_client.health_check()
                    go_service_status = "healthy"
                except Exception as e:
                    go_service_status = f"unhealthy: {str(e)}"
            
            status = {
                "status": "healthy" if go_service_status == "healthy" else "degraded",
                "timestamp": asyncio.get_event_loop().time(),
                "components": {
                    "go_service": go_service_status,
                    "data_processor": "healthy" if self.data_processor else "not_initialized",
                    "tools": f"loaded ({len(self.tools)} tools)" if self.tools else "not_loaded"
                },
                "tools_available": list(self.tools.keys()) if self.tools else [],
                "server_info": {
                    "name": settings.server_name,
                    "version": settings.server_version
                }
            }
            
            logger.debug("Health check completed", status=status["status"])
            return status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        try:
            info = {
                "server": {
                    "name": settings.server_name,
                    "version": settings.server_version,
                    "description": "Academic Research MCP Server - MVP Version"
                },
                "tools": {
                    "total_count": len(self.tools),
                    "available_tools": list(self.tools.keys()),
                    "categories": {
                        "author_tools": ["search_authors", "get_author_details"],
                        "paper_tools": ["search_papers", "get_paper_details", "get_paper_citations", "get_trending_papers"],
                        "network_tools": ["get_citation_network", "get_collaboration_network"],
                        "trend_tools": ["get_top_keywords", "analyze_domain_trends"]
                    }
                },
                "backend": {
                    "go_service_url": settings.go_service_url,
                    "connection_status": "connected" if self.go_client else "disconnected"
                }
            }
            
            # 尝试获取Go服务信息
            if self.go_client:
                try:
                    go_info = await self.go_client.get_service_info()
                    info["backend"]["go_service_info"] = go_info
                except Exception as e:
                    info["backend"]["go_service_error"] = str(e)
            
            return info
            
        except Exception as e:
            logger.error("Failed to get server info", error=str(e))
            return {
                "error": str(e),
                "server": {
                    "name": settings.server_name,
                    "version": settings.server_version
                }
            }
    
    async def cleanup(self):
        """清理服务器资源"""
        logger.info("Starting server cleanup")
        
        try:
            # 清理Go客户端
            if self.go_client:
                await self.go_client.disconnect()
                self.go_client = None
                logger.debug("Go client cleaned up")
            
            # 清理工具注册表
            self.tools.clear()
            self.tool_definitions.clear()
            
            # 清理数据处理器
            self.data_processor = None
            
            logger.info("Server cleanup completed successfully")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
            raise

# 便捷函数用于创建和运行服务器
async def create_server() -> AcademicMCPServer:
    """创建并初始化MCP服务器"""
    server = AcademicMCPServer()
    await server.initialize()
    return server

async def run_server():
    """运行MCP服务器的便捷函数"""
    server = None
    try:
        server = await create_server()
        logger.info("MCP Server started successfully")
        
        # 这里可以添加服务器运行逻辑
        # 例如等待信号或运行事件循环
        
    except Exception as e:
        logger.error("Failed to start MCP server", error=str(e))
        raise
    finally:
        if server:
            await server.cleanup()

if __name__ == "__main__":
    # 用于直接运行测试
    import asyncio
    asyncio.run(run_server())