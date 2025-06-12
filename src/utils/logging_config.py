import logging
import logging.handlers
import os
import structlog
from typing import Optional, Any
from ..config import settings

class CustomLogger:
    """自定义Logger类，支持error参数和structlog风格"""
    
    def __init__(self, name: Optional[str] = None):
        self._logger = logging.getLogger(name or __name__)
        self._struct_logger = structlog.get_logger(name or __name__)
        
        # 确保logger级别正确设置
        log_level = getattr(logging, settings.log_level.upper(), logging.DEBUG)
        self._logger.setLevel(log_level)
    
    def _format_message_with_kwargs(self, message: str, **kwargs) -> str:
        """将kwargs格式化到消息中"""
        if kwargs:
            kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} [{kwargs_str}]"
        return message
    
    def debug(self, message: str, error: Optional[Any] = None, **kwargs):
        """调试日志"""
        if error:
            formatted_msg = self._format_message_with_kwargs(f"{message}: {error}", **kwargs)
            self._logger.debug(formatted_msg)
            self._struct_logger.debug(message, error=str(error), **kwargs)
        else:
            formatted_msg = self._format_message_with_kwargs(message, **kwargs)
            self._logger.debug(formatted_msg)
            self._struct_logger.debug(message, **kwargs)
    
    def info(self, message: str, error: Optional[Any] = None, **kwargs):
        """信息日志 - 兼容structlog风格"""
        if error:
            formatted_msg = self._format_message_with_kwargs(f"{message}: {error}", **kwargs)
            self._logger.info(formatted_msg)
            self._struct_logger.info(message, error=str(error), **kwargs)
        elif kwargs:
            # 如果有其他参数，使用structlog风格
            self._struct_logger.info(message, **kwargs)
            # 同时也用标准logger记录（不传递kwargs）
            formatted_msg = self._format_message_with_kwargs(message, **kwargs)
            self._logger.info(formatted_msg)
        else:
            self._logger.info(message)
            self._struct_logger.info(message)
    
    def warning(self, message: str, error: Optional[Any] = None, **kwargs):
        """警告日志"""
        if error:
            formatted_msg = self._format_message_with_kwargs(f"{message}: {error}", **kwargs)
            self._logger.warning(formatted_msg)
            self._struct_logger.warning(message, error=str(error), **kwargs)
        elif kwargs:
            self._struct_logger.warning(message, **kwargs)
            formatted_msg = self._format_message_with_kwargs(message, **kwargs)
            self._logger.warning(formatted_msg)
        else:
            self._logger.warning(message)
            self._struct_logger.warning(message)
    
    def error(self, message: str, error: Optional[Any] = None, **kwargs):
        """错误日志"""
        if error:
            formatted_msg = self._format_message_with_kwargs(f"{message}: {error}", **kwargs)
            self._logger.error(formatted_msg, exc_info=True)
            self._struct_logger.error(message, error=str(error), **kwargs)
        elif kwargs:
            self._struct_logger.error(message, **kwargs)
            formatted_msg = self._format_message_with_kwargs(message, **kwargs)
            self._logger.error(formatted_msg)
        else:
            self._logger.error(message)
            self._struct_logger.error(message)
    
    def critical(self, message: str, error: Optional[Any] = None, **kwargs):
        """严重错误日志"""
        if error:
            formatted_msg = self._format_message_with_kwargs(f"{message}: {error}", **kwargs)
            self._logger.critical(formatted_msg, exc_info=True)
            self._struct_logger.critical(message, error=str(error), **kwargs)
        elif kwargs:
            self._struct_logger.critical(message, **kwargs)
            formatted_msg = self._format_message_with_kwargs(message, **kwargs)
            self._logger.critical(formatted_msg)
        else:
            self._logger.critical(message)
            self._struct_logger.critical(message)
    
    def exception(self, message: str, **kwargs):
        """异常日志（自动包含堆栈信息）"""
        formatted_msg = self._format_message_with_kwargs(message, **kwargs)
        self._logger.exception(formatted_msg)
        self._struct_logger.exception(message, **kwargs)

def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    if settings.log_file:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # 获取日志级别
    log_level = getattr(logging, settings.log_level.upper(), logging.DEBUG)
    
    # 创建处理器列表
    handlers = []
    
    # 文件处理器
    if settings.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file,
            maxBytes=settings.log_max_size,
            backupCount=settings.log_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # 配置标准日志
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # 强制重新配置
    )
    
    # 设置根logger级别
    logging.getLogger().setLevel(log_level)
    
    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 验证日志配置
    test_logger = logging.getLogger("setup_test")
    test_logger.debug("Debug logging is enabled")
    test_logger.info(f"Logging setup completed - Level: {settings.log_level}")
    
    print(f"=== 日志配置信息 ===")
    print(f"日志级别: {settings.log_level} ({log_level})")
    print(f"日志文件: {settings.log_file}")
    print(f"根logger级别: {logging.getLogger().level}")
    print(f"处理器数量: {len(handlers)}")
    for i, handler in enumerate(handlers):
        print(f"  处理器{i}: {type(handler).__name__} - 级别: {handler.level}")

def get_logger(name: Optional[str] = None) -> CustomLogger:
    """获取自定义日志记录器"""
    return CustomLogger(name)

# 为了兼容现有代码，也提供structlog的获取方式
def get_struct_logger(name: Optional[str] = None):
    """获取structlog记录器"""
    return structlog.get_logger(name)

# 初始化日志
setup_logging()
