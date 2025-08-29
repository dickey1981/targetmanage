"""
应用配置设置
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "目标管理系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 数据库配置（使用同一个数据库）
    # 生产环境：腾讯云LightDB MySQL 5.7 (外网访问)
    DATABASE_URL: str = "mysql+pymysql://root:targetM123@sh-cynosdbmysql-grp-hocwbafo.sql.tencentcdb.com:26153/targetmanage"
    DATABASE_TEST_URL: str = "mysql+pymysql://root:targetM123@sh-cynosdbmysql-grp-hocwbafo.sql.tencentcdb.com:26153/targetmanage"
    
    # 本地开发数据库配置（可选）
    LOCAL_DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/targetmanage"
    USE_LOCAL_DB: bool = False  # 设置为True使用本地数据库
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1小时
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".mp3", ".wav", ".m4a"]
    
    # 微信小程序配置
    # 请替换为您的实际微信小程序AppID和AppSecret
    WECHAT_APP_ID: str = "wxe0c0f4327a75c33f"  # 例如：wx1234567890abcdef
    WECHAT_APP_SECRET: str = "7757cc7f7b9c819cfd4db042176f1698"  # 例如：abcdef1234567890abcdef1234567890
    WECHAT_SESSION_KEY_EXPIRE: int = 7200  # 2小时
    
    # AI服务配置
    # 百度OCR
    BAIDU_OCR_API_KEY: str = ""
    BAIDU_OCR_SECRET_KEY: str = ""
    
    # 百度语音
    BAIDU_SPEECH_API_KEY: str = ""
    BAIDU_SPEECH_SECRET_KEY: str = ""
    
    # 腾讯云配置
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_REGION: str = "ap-beijing"
    
    # 腾讯云COS配置
    COS_BUCKET_NAME: str = ""
    COS_REGION: str = "ap-beijing"
    COS_DOMAIN: str = ""
    
    # 腾讯云CLS日志服务
    CLS_REGION: str = "ap-beijing"
    CLS_TOPIC_ID: str = ""
    CLS_SECRET_ID: str = ""
    CLS_SECRET_KEY: str = ""
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 邮件配置
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    
    # 密码策略
    MIN_PASSWORD_LENGTH: int = 8
    PASSWORD_COMPLEXITY: bool = True
    
    # 登录策略
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION: int = 15  # 分钟
    SESSION_TIMEOUT: int = 30  # 分钟
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """获取设置实例"""
    return Settings()


# 创建设置实例
settings = get_settings()
