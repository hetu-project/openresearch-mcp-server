#!/usr/bin/env python3
"""
OpenResearch MCP Server - 学术研究工具的MCP服务器
主入口点
"""
import asyncio
import sys
import signal
from typing import Optional
import structlog

from src.server import AcademicMCPServer
from src.utils.logging_config import setup_logging

# 设置日志
setup_logging()
logger = structlog.get_logger()

class ServerManager:
    """服务器管理器，负责服务器的生命周期管理"""
    
    def __init__(self):
        self.server_instance: Optional[AcademicMCPServer] = None
        self._shutdown_event = asyncio.Event()
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal", signal=signum)
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_server(self):
        """启动服务器"""
        try:
            logger.info("Starting OpenResearch MCP Server")
            
            # 创建服务器实例
            self.server_instance = AcademicMCPServer()
            
            # 初始化服务器
            await self.server_instance.initialize()
            
            # 确保 go_client 已初始化
            if self.server_instance.go_client is None:
                raise RuntimeError("Go client not initialized")
            
            logger.info("Academic MCP Server is ready")
            
            # 使用 stdio 作为默认的输入输出流
            from mcp.server.stdio import stdio_server
            
            async with self.server_instance.go_client:
                # 使用 stdio_server 运行 MCP 服务器
                async with stdio_server() as (read_stream, write_stream):
                    # 使用服务器的内置方法创建初始化选项
                    init_options = self.server_instance.server.create_initialization_options()
                    
                    # 创建服务器运行任务
                    server_task = asyncio.create_task(
                        self.server_instance.server.run(
                            read_stream=read_stream,
                            write_stream=write_stream,
                            initialization_options=init_options
                        )
                    )
                    
                    # 等待关闭信号或服务器完成
                    shutdown_task = asyncio.create_task(
                        self._shutdown_event.wait()
                    )
                    
                    done, pending = await asyncio.wait(
                        [server_task, shutdown_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # 取消未完成的任务
                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    
                    # 检查是否有异常
                    for task in done:
                        exception = task.exception()
                        if exception is not None:
                            raise exception
                            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error("Server startup failed", error=str(e))
            raise
        finally:
            await self.cleanup()


    
    async def cleanup(self):
        """清理资源"""
        if self.server_instance:
            await self.server_instance.cleanup()
        logger.info("Server shutdown completed")

async def main():
    """主函数"""
    manager = ServerManager()
    manager.setup_signal_handlers()
    
    try:
        await manager.start_server()
    except Exception as e:
        logger.error("Application error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted")
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        sys.exit(1)