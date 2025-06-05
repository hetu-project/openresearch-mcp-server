"""
工具模块

提供错误处理、日志配置等通用工具功能。
"""

from .error_handler import (
    handle_tool_error,
    AcademicMCPError,
    DataProcessingError,
    ServiceConnectionError,
    ValidationError
)
from .logging_config import setup_logging

# 导出主要功能
__all__ = [
    # 错误处理
    "handle_tool_error",
    "AcademicMCPError", 
    "DataProcessingError",
    "ServiceConnectionError",
    "ValidationError",
    
    # 日志配置
    "setup_logging",
]
