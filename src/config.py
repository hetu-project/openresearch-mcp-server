"""
配置管理模块
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """应用配置类"""
    
    # 服务器配置
    server_name: str = Field(default="OpenResearch MCP Server", description="服务器名称")
    server_version: str = Field(default="1.0.0", description="服务器版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # Go 服务配置
    go_service_url: str = Field(default="https://test.nftkash.xyz/neo4j", description="Go服务地址")
    go_service_timeout: int = Field(default=30, description="Go服务超时时间(秒)")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    
    # API配置
    max_results: int = Field(default=100, description="最大返回结果数")
    cache_ttl: int = Field(default=3600, description="缓存TTL(秒)")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# 创建全局配置实例
settings = Settings()
