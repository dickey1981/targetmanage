#!/usr/bin/env python3
"""
修复外键约束
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_foreign_key_constraints():
    """修复外键约束"""
    try:
        db = next(get_db())
        
        # 删除现有的外键约束
        try:
            db.execute(text("ALTER TABLE process_records DROP FOREIGN KEY process_records_ibfk_1"))
            logger.info("✅ 删除user_id外键约束成功")
        except Exception as e:
            logger.info(f"删除user_id外键约束失败（可能不存在）: {e}")
        
        try:
            db.execute(text("ALTER TABLE process_records DROP FOREIGN KEY process_records_ibfk_2"))
            logger.info("✅ 删除goal_id外键约束成功")
        except Exception as e:
            logger.info(f"删除goal_id外键约束失败（可能不存在）: {e}")
        
        # 添加新的外键约束
        try:
            db.execute(text("ALTER TABLE process_records ADD CONSTRAINT fk_process_records_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"))
            db.commit()
            logger.info("✅ 添加user_id外键约束成功")
        except Exception as e:
            logger.error(f"添加user_id外键约束失败: {e}")
        
        try:
            db.execute(text("ALTER TABLE process_records ADD CONSTRAINT fk_process_records_goal_id FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL"))
            db.commit()
            logger.info("✅ 添加goal_id外键约束成功")
        except Exception as e:
            logger.error(f"添加goal_id外键约束失败: {e}")
        
    except Exception as e:
        logger.error(f"❌ 修复外键约束失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始修复外键约束...")
    fix_foreign_key_constraints()
    logger.info("🎉 外键约束修复完成！")

if __name__ == "__main__":
    main()
