#!/usr/bin/env python3
"""
OpenResearch MCP Server - MCP server for academic research tools
Main entry point - Fixed version
"""
import asyncio
import sys
import signal
from typing import Optional
import structlog
from pathlib import Path
import os

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure current working directory is project root
os.chdir(project_root)

from src.server import AcademicMCPServer
from src.utils.logging_config import setup_logging,get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__) 

async def main():
    """Main function - Fixed version"""
    server = None
    
    try:
        logger.info("Starting OpenResearch MCP Server")
        
        # Create and initialize server
        server = AcademicMCPServer()
        await server.initialize()
        
        # Ensure go_client is initialized
        if server.go_client is None:
            raise RuntimeError("Go client not initialized")
        
        logger.info("Academic MCP Server is ready")
        
        # Run MCP server - Using go_client's async context manager
        from mcp.server.stdio import stdio_server
        from mcp.server.models import InitializationOptions
        from mcp.types import ServerCapabilities, ToolsCapability
        
        # Create initialization options
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