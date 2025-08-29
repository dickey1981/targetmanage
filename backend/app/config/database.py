"""
数据库配置
Database configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .settings import get_settings

settings = get_settings()

# 数据库连接URL
# 根据配置选择使用本地还是远程数据库
if settings.USE_LOCAL_DB:
    DATABASE_URL = settings.LOCAL_DATABASE_URL
    print(f"🔧 使用本地数据库: {DATABASE_URL}")
else:
    DATABASE_URL = settings.DATABASE_URL
    print(f"☁️ 使用远程数据库: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    # 连接池配置
    poolclass=QueuePool,
    pool_size=20,           # 连接池大小
    max_overflow=30,        # 最大溢出连接数
    pool_timeout=30,        # 获取连接超时时间
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True,     # 连接前ping检查
    # 性能优化
    echo=settings.DEBUG,    # 开发环境显示SQL日志
    echo_pool=False,        # 关闭连接池日志
    # MySQL特定配置
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

# 依赖函数：获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
