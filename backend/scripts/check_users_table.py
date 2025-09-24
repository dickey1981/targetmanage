#!/usr/bin/env python3
"""
检查users表结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_users_table():
    """检查users表结构"""
    try:
        db = next(get_db())
        
        # 检查users表结构
        result = db.execute(text("DESCRIBE users"))
        columns = result.fetchall()
        logger.info("users表结构:")
        for column in columns:
            logger.info(f"  {column[0]} - {column[1]} - {column[2]}")
        
        # 检查是否有数据
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.fetchone()[0]
        logger.info(f"users表记录数: {count}")
        
        if count == 0:
            # 插入测试用户
            db.execute(text("INSERT INTO users (id, username, email, created_at, updated_at, is_deleted) VALUES (1, 'test_user', 'test@example.com', NOW(), NOW(), FALSE)"))
            db.commit()
            logger.info("✅ 插入测试用户成功")
        
    except Exception as e:
        logger.error(f"❌ 检查users表失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始检查users表...")
    check_users_table()
    logger.info("🎉 users表检查完成！")

if __name__ == "__main__":
    main()
