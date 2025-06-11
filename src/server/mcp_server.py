"""
Academic Research MCP Server Core Implementation - Revised Version
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
    """Academic Research MCP Server - Revised Version"""
    
    def __init__(self):
        self.server = Server(settings.server_name)
        self.go_client: Optional[GoServiceClient] = None
        self.data_processor: Optional[DataProcessor] = None
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: list[Tool] = []
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register handlers using MCP decorators"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools"""
            logger.debug("Listing available tools", tool_count=len(self.tool_definitions))
            return self.tool_definitions
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None = None) -> list[TextContent]:
            """Call specified tool"""
            arguments = arguments or {}
            
            logger.info(
                "Executing tool",
                tool_name=name,
                arguments=arguments
            )
            
            if name not in self.tools:
                error_msg = f"Unknown tool: {name}. Available tools: {list(self.tools.keys())}"
                logger.error("Tool not found", tool_name=name)
                raise ValueError(error_msg)
            
            try:
                result = await self.tools[name](arguments)
                
                logger.info(
                    "Tool executed successfully",
                    tool_name=name,
                    result_type=type(result).__name__,
                    result_count=len(result) if isinstance(result, list) else 1
                )
                
                if isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
                    return result
                elif isinstance(result, list):
                    return [TextContent(type="text", text=str(item)) for item in result]
                else:
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
        """Initialize server components"""
        logger.info("Initializing Academic MCP Server components")
        
        try:
            await self._initialize_core_components()
            
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
        """Initialize core components"""
        self.go_client = GoServiceClient()
        
        self.data_processor = DataProcessor()
        
        logger.debug("Core components initialized")
    
    async def _initialize_tools(self):
        """Initialize all tools"""
        assert self.go_client is not None, "GoServiceClient must be initialized before tools"
        assert self.data_processor is not None, "DataProcessor must be initialized before tools"

        try:
            self.tools = create_tool_registry(self.go_client, self.data_processor)
            
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
        """Clean up server resources"""
        logger.info("Starting server cleanup")
        
        try:
            self.go_client = None
            
            self.tools.clear()
            self.tool_definitions.clear()
            
            self.data_processor = None
            
            logger.info("Server cleanup completed successfully")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
            raise