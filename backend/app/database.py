"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# 从配置获取数据库URL
from .config.settings import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎（MySQL配置）
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # 生产环境设为False
    connect_args={
        "charset": "utf8mb4",
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO",
        "autocommit": False
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """删除数据库表"""
    Base.metadata.drop_all(bind=engine)