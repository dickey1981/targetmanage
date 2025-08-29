#!/usr/bin/env python3
"""
简单的数据库初始化脚本
直接使用SQL创建表，避免模型关系问题
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config.settings import get_settings

def init_database():
    """初始化数据库"""
    try:
        # 获取配置
        print("🔍 获取数据库配置...")
        settings = get_settings()
        database_url = settings.DATABASE_URL
        
        print(f"🔍 数据库URL: {database_url}")
        
        # 创建数据库引擎
        print("🔍 创建数据库引擎...")
        engine = create_engine(database_url)
        
        # 测试连接
        print("🔍 测试数据库连接...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
        
        # 创建表
        print("🔨 开始创建数据库表...")
        
        with engine.connect() as conn:
            # 创建users表
            print("🔨 创建users表...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    wechat_id VARCHAR(100) UNIQUE NOT NULL,
                    nickname VARCHAR(100) NOT NULL,
                    avatar TEXT,
                    phone_number VARCHAR(20),
                    email VARCHAR(100),
                    notification_enabled BOOLEAN DEFAULT TRUE,
                    privacy_level VARCHAR(20) DEFAULT 'public',
                    total_goals VARCHAR(10) DEFAULT '0',
                    completed_goals VARCHAR(10) DEFAULT '0',
                    streak_days VARCHAR(10) DEFAULT '0',
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_locked BOOLEAN DEFAULT FALSE,
                    locked_until DATETIME,
                    failed_login_attempts VARCHAR(10) DEFAULT '0',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login_at DATETIME,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    deleted_at DATETIME
                )
            """))
            print("✅ users表创建成功")
            
            # 创建goals表
            print("🔨 创建goals表...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    category VARCHAR(50) DEFAULT 'personal',
                    priority VARCHAR(20) DEFAULT 'medium',
                    status VARCHAR(20) DEFAULT 'draft',
                    start_date DATETIME,
                    end_date DATETIME,
                    estimated_hours FLOAT,
                    progress_percentage FLOAT DEFAULT 0.0,
                    is_completed BOOLEAN DEFAULT FALSE,
                    completed_at DATETIME,
                    is_public BOOLEAN DEFAULT FALSE,
                    allow_collaboration BOOLEAN DEFAULT FALSE,
                    reminder_enabled BOOLEAN DEFAULT TRUE,
                    reminder_frequency VARCHAR(20) DEFAULT 'daily',
                    user_id INT NOT NULL,
                    parent_goal_id INT,
                    total_tasks INT DEFAULT 0,
                    completed_tasks INT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            print("✅ goals表创建成功")
            
            conn.commit()
        
        print("🎉 数据库初始化完成！")
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库操作失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 启动数据库初始化脚本...")
    init_database()
    print("✅ 脚本执行完成")
