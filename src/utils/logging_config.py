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
    
    def debug(self, message: str, error: Optional[Any] = None, **kwargs):
        """调试日志"""
        if error:
            self._logger.debug(f"{message}: {error}", **kwargs)
        else:
            self._logger.debug(message, **kwargs)
    
    def info(self, message: str, error: Optional[Any] = None, **kwargs):
        """信息日志 - 兼容structlog风格"""
        if error:
            self._logger.info(f"{message}: {error}", **kwargs)
        elif kwargs:
            # 如果有其他参数，使用structlog风格
            self._struct_logger.info(message, **kwargs)
        else:
            self._logger.info(message)
    
    def warning(self, message: str, error: Optional[Any] = None, **kwargs):
        """警告日志"""
        if error:
            self._logger.warning(f"{message}: {error}", **kwargs)
        elif kwargs:
            self._struct_logger.warning(message, **kwargs)
        else:
            self._logger.warning(message)
    
    def error(self, message: str, error: Optional[Any] = None, **kwargs):
        """错误日志"""
        if error:
            self._logger.error(f"{message}: {error}", exc_info=True, **kwargs)
        elif kwargs:
            self._struct_logger.error(message, **kwargs)
        else:
            self._logger.error(message, **kwargs)
    
    def critical(self, message: str, error: Optional[Any] = None, **kwargs):
        """严重错误日志"""
        if error:
            self._logger.critical(f"{message}: {error}", exc_info=True, **kwargs)
        elif kwargs:
            self._struct_logger.critical(message, **kwargs)
        else:
            self._logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """异常日志（自动包含堆栈信息）"""
        self._logger.exception(message, **kwargs)

def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    if settings.log_file:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # 配置标准日志
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.DEBUG),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                settings.log_file,
                maxBytes=settings.log_max_size,
                backupCount=settings.log_backup_count,
                encoding='utf-8'
            ) if settings.log_file else logging.NullHandler(),
            logging.StreamHandler()
        ]
    )
    
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

def get_logger(name: Optional[str] = None) -> CustomLogger:
    """获取自定义日志记录器"""
    return CustomLogger(name)

# 为了兼容现有代码，也提供structlog的获取方式
def get_struct_logger(name: Optional[str] = None):
    """获取structlog记录器"""
    return structlog.get_logger(name)

# 初始化日志
setup_logging()
