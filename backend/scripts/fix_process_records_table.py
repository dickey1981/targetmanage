#!/usr/bin/env python3
"""
修复过程记录表结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_process_records_table():
    """修复过程记录表结构"""
    try:
        db = next(get_db())
        
        # 检查并添加 is_deleted 字段
        try:
            db.execute(text("ALTER TABLE process_records ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除'"))
            db.commit()
            logger.info("✅ 添加 is_deleted 字段成功")
        except Exception as e:
            if "Duplicate column name" in str(e):
                logger.info("is_deleted 字段已存在，跳过添加")
            else:
                logger.error(f"添加 is_deleted 字段失败: {e}")
        
        # 检查表结构
        result = db.execute(text("DESCRIBE process_records"))
        columns = result.fetchall()
        logger.info("当前表结构:")
        for column in columns:
            logger.info(f"  {column[0]} - {column[1]} - {column[2]}")
        
    except Exception as e:
        logger.error(f"❌ 修复表结构失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始修复过程记录表结构...")
    fix_process_records_table()
    logger.info("🎉 表结构修复完成！")

if __name__ == "__main__":
    main()
