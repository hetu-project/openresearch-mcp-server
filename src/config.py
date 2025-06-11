"""
Configuration Management Module
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application Configuration Class"""
    
    # Server Configuration
    server_name: str = Field(default="OpenResearch MCP Server", description="SERVER_NAME")
    server_version: str = Field(default="1.0.0", description="SERVER_VERSION")
    debug: bool = Field(default=False, description="DEBUG")
    
    # Go Service Configuration
    go_service_url: str = Field(default="https://test.nftkash.xyz/neo4j", description="GO_SERVICE_URL")
    go_service_timeout: int = Field(default=30, description="GO_SERVICE_TIMEOUT")
    
    # Log Configuration
    log_level: str = Field(default="DEBUG", description="LOG_LEVEL")
    log_file: Optional[str] = Field(default="logs/mcp_debug.log", description="LOG_FILE")
    log_max_size: int = Field(default=10485760, description="LOG_MAX_SIZE")  # 10MB
    log_backup_count: int = Field(default=5, description="LOG_BACKUP_COUNT")

    # API Configuration
    max_results: int = Field(default=100, description="MAX_RESULTS")
    cache_ttl: int = Field(default=3600, description="CACHE_TTL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Create Global Configuration Instance
settings = Settings()