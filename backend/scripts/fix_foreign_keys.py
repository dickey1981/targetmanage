#!/usr/bin/env python3
"""
修复外键类型不匹配问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_foreign_keys():
    """修复外键类型不匹配问题"""
    try:
        db = next(get_db())
        
        # 修改process_records表的user_id字段类型
        try:
            db.execute(text("ALTER TABLE process_records MODIFY COLUMN user_id VARCHAR(36) NOT NULL COMMENT '用户ID'"))
            db.commit()
            logger.info("✅ 修改user_id字段类型成功")
        except Exception as e:
            logger.error(f"修改user_id字段类型失败: {e}")
        
        # 修改process_records表的goal_id字段类型
        try:
            db.execute(text("ALTER TABLE process_records MODIFY COLUMN goal_id VARCHAR(36) COMMENT '目标ID'"))
            db.commit()
            logger.info("✅ 修改goal_id字段类型成功")
        except Exception as e:
            logger.error(f"修改goal_id字段类型失败: {e}")
        
        # 检查表结构
        result = db.execute(text("DESCRIBE process_records"))
        columns = result.fetchall()
        logger.info("修改后的process_records表结构:")
        for column in columns:
            if column[0] in ['user_id', 'goal_id']:
                logger.info(f"  {column[0]} - {column[1]} - {column[2]}")
        
    except Exception as e:
        logger.error(f"❌ 修复外键失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始修复外键类型...")
    fix_foreign_keys()
    logger.info("🎉 外键修复完成！")

if __name__ == "__main__":
    main()
