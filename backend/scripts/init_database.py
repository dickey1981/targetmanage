#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库、用户和表结构
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import get_settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """创建数据库"""
    settings = get_settings()
    
    # 解析数据库URL
    db_url = settings.DATABASE_URL
    db_parts = db_url.replace("postgresql://", "").split("/")
    db_host_port = db_parts[0].split(":")
    db_host = db_host_port[0]
    db_port = int(db_host_port[1]) if len(db_host_port) > 1 else 5432
    db_user_pass = db_parts[0].split("@")[0].split(":")
    db_user = db_user_pass[0]
    db_password = db_user_pass[1] if len(db_user_pass) > 1 else ""
    db_name = db_parts[1]
    
    try:
        # 连接到PostgreSQL服务器
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"  # 连接到默认数据库
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"数据库 {db_name} 创建成功")
        else:
            logger.info(f"数据库 {db_name} 已存在")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"创建数据库失败: {e}")
        return False

def create_tables():
    """创建表结构"""
    try:
        from app.database import engine
        from app.models.user import Base as UserBase
        from app.models.session import Base as SessionBase
        
        # 创建所有表
        UserBase.metadata.create_all(bind=engine)
        SessionBase.metadata.create_all(bind=engine)
        
        logger.info("表结构创建成功")
        return True
        
    except Exception as e:
        logger.error(f"创建表结构失败: {e}")
        return False

def run_migrations():
    """运行数据库迁移"""
    try:
        import subprocess
        import os
        
        # 切换到backend目录
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(backend_dir)
        
        # 运行Alembic迁移
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir
        )
        
        if result.returncode == 0:
            logger.info("数据库迁移成功")
            return True
        else:
            logger.error(f"数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"运行数据库迁移失败: {e}")
        return False

def create_initial_data():
    """创建初始数据"""
    try:
        from app.database import SessionLocal
        from app.models.user import User
        from datetime import datetime
        import uuid
        
        db = SessionLocal()
        
        # 检查是否已有用户
        existing_user = db.query(User).first()
        if existing_user:
            logger.info("数据库中已有用户数据，跳过初始数据创建")
            db.close()
            return True
        
        # 创建测试用户
        test_user = User(
            id=uuid.uuid4(),
            wechat_id="test_wechat_id",
            nickname="测试用户",
            avatar="https://example.com/avatar.jpg",
            phone_number="13800138000",
            email="test@example.com",
            notification_enabled=True,
            privacy_level="public",
            total_goals="0",
            completed_goals="0",
            streak_days="0",
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(test_user)
        db.commit()
        db.close()
        
        logger.info("初始数据创建成功")
        return True
        
    except Exception as e:
        logger.error(f"创建初始数据失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始初始化数据库...")
    
    # 1. 创建数据库
    if not create_database():
        logger.error("数据库创建失败，退出")
        sys.exit(1)
    
    # 2. 创建表结构
    if not create_tables():
        logger.error("表结构创建失败，退出")
        sys.exit(1)
    
    # 3. 运行迁移
    if not run_migrations():
        logger.error("数据库迁移失败，退出")
        sys.exit(1)
    
    # 4. 创建初始数据
    if not create_initial_data():
        logger.error("初始数据创建失败，退出")
        sys.exit(1)
    
    logger.info("数据库初始化完成！")

if __name__ == "__main__":
    main()
