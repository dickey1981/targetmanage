#!/usr/bin/env python3
"""
检查数据库表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables():
    """检查数据库表"""
    try:
        db = next(get_db())
        
        # 获取所有表
        result = db.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        
        logger.info("数据库中的表:")
        for table in tables:
            logger.info(f"  {table[0]}")
        
        # 检查关键表是否存在
        table_names = [table[0] for table in tables]
        
        if 'users' in table_names:
            logger.info("✅ users 表存在")
        else:
            logger.info("❌ users 表不存在")
            
        if 'goals' in table_names:
            logger.info("✅ goals 表存在")
        else:
            logger.info("❌ goals 表不存在")
            
        if 'process_records' in table_names:
            logger.info("✅ process_records 表存在")
        else:
            logger.info("❌ process_records 表不存在")
        
    except Exception as e:
        logger.error(f"❌ 检查表失败: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始检查数据库表...")
    check_tables()
    logger.info("🎉 表检查完成！")

if __name__ == "__main__":
    main()
