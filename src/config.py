# src/config.py
from typing import Optional
from pydantic import BaseSettings, Field
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    server_name: str = Field(default="academic-mcp-server", env="SERVER_NAME")
    server_version: str = Field(default="0.1.0", env="SERVER_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Go服务配置
    go_service_base_url: str = Field(
        default="http://localhost:8080", 
        env="GO_SERVICE_BASE_URL"
    )
    go_service_timeout: int = Field(default=30, env="GO_SERVICE_TIMEOUT")
    go_service_max_retries: int = Field(default=3, env="GO_SERVICE_MAX_RETRIES")
    
    # 缓存配置
    #redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    enable_cache: bool = True
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1小时
    
    # 限流配置
    # rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    # rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()
