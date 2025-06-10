#!/usr/bin/env python3
"""
OpenResearch MCP Server - 学术研究工具的MCP服务器
主入口点 - 修正版本
"""
import asyncio
import sys
import signal
from typing import Optional
import structlog
from pathlib import Path
import os

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保当前工作目录是项目根目录
os.chdir(project_root)

from src.server import AcademicMCPServer
from src.utils.logging_config import setup_logging,get_logger

# 设置日志
setup_logging()
logger = get_logger(__name__) 

async def main():
    """主函数 - 修正版本"""
    server = None
    
    try:
        logger.info("Starting OpenResearch MCP Server")
        
        # 创建并初始化服务器
        server = AcademicMCPServer()
        await server.initialize()
        
        # 确保 go_client 已初始化
        if server.go_client is None:
            raise RuntimeError("Go client not initialized")
        
        logger.info("Academic MCP Server is ready")
        
        # 运行 MCP 服务器 - 使用 go_client 的异步上下文管理器
        from mcp.server.stdio import stdio_server
        from mcp.server.models import InitializationOptions
        from mcp.types import ServerCapabilities, ToolsCapability
        
        # 创建初始化选项
        init_options = InitializationOptions(
            server_name=server.server.name,
            server_version="1.0.0",
            capabilities=ServerCapabilities(
                tools=ToolsCapability(listChanged=False)
            )
        )
        
        async with server.go_client:
            async with stdio_server() as (read_stream, write_stream):
                await server.server.run(
                    read_stream,
                    write_stream,
                    init_options
                )
                
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        sys.exit(1)
    finally:
        if server:
            await server.cleanup()
        logger.info("Server shutdown completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted")
    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        sys.exit(1)
