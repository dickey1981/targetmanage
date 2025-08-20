"""
数据库配置和连接
Database configuration and connection
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis

from app.config.settings import settings

# SQLAlchemy配置
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    # 连接池配置
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()

# Redis连接
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_redis():
    """获取Redis连接"""
    return redis_client


async def create_tables():
    """创建数据库表"""
    # 导入所有模型以确保它们被注册
    from app.models import user, goal, task, progress
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)


async def drop_tables():
    """删除所有数据库表（仅用于测试）"""
    Base.metadata.drop_all(bind=engine)


# 数据库连接测试
async def test_db_connection():
    """测试数据库连接"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


# Redis连接测试
async def test_redis_connection():
    """测试Redis连接"""
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis连接失败: {e}")
        return False
