"""
应用配置设置
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    APP_NAME: str = "@numericalTools"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "通用数值模拟验证工具"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 数据库配置（可选）
    DATABASE_URL: Optional[str] = None
    
    # 模拟配置
    MAX_SIMULATION_ROUNDS: int = 10_000_000
    MAX_CONCURRENT_SIMULATIONS: int = 5
    DEFAULT_TIMEOUT: int = 300  # 5分钟
    
    # 文件存储
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    TEMP_DIR: str = "temp"
    
    # 安全配置
    SECRET_KEY: str = "numerical-tools-secret-key-2025"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    ALLOWED_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()

# 确保必要的目录存在
for directory in [settings.UPLOAD_DIR, settings.REPORTS_DIR, settings.TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)
