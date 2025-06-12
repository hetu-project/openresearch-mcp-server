# src/utils/error_handler.py
import functools
import structlog
from typing import Callable, Any, List
from mcp.types import TextContent

logger = structlog.get_logger()

def handle_tool_error(func: Callable) -> Callable:
    """工具错误处理装饰器"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> List[TextContent]:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                "Tool execution error",
                tool_name=func.__name__,
                error=str(e),
                exc_info=True
            )
            
            error_message = f"工具执行失败: {str(e)}"
            return [TextContent(type="text", text=error_message)]
    
    return wrapper

class AcademicMCPError(Exception):
    """学术MCP基础异常"""
    pass

class DataProcessingError(AcademicMCPError):
    """数据处理异常"""
    pass

class ServiceConnectionError(AcademicMCPError):
    """服务连接异常"""
    pass

class ValidationError(AcademicMCPError):
    """数据验证异常"""
    pass
