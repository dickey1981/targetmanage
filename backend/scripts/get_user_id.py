#!/usr/bin/env python3
"""
获取用户ID
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_id():
    """获取用户ID"""
    try:
        db = next(get_db())
        
        # 获取第一个用户ID
        result = db.execute(text("SELECT id FROM users LIMIT 1"))
        user = result.fetchone()
        
        if user:
            logger.info(f"找到用户ID: {user[0]}")
            return user[0]
        else:
            logger.info("没有找到用户")
            return None
        
    except Exception as e:
        logger.error(f"❌ 获取用户ID失败: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始获取用户ID...")
    user_id = get_user_id()
    logger.info(f"🎉 用户ID: {user_id}")

if __name__ == "__main__":
    main()
