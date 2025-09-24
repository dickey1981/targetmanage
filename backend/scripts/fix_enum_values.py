#!/usr/bin/env python3
"""
修复枚举值
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_enum_values():
    """修复枚举值"""
    try:
        db = next(get_db())
        
        # 修改record_type枚举值
        try:
            db.execute(text("ALTER TABLE process_records MODIFY COLUMN record_type ENUM('progress', 'process', 'milestone', 'difficulty', 'method', 'reflection', 'adjustment', 'achievement', 'insight', 'other') DEFAULT 'process' COMMENT '记录类型'"))
            db.commit()
            logger.info("✅ 修改record_type枚举值成功")
        except Exception as e:
            logger.error(f"修改record_type枚举值失败: {e}")
        
        # 修改source枚举值
        try:
            db.execute(text("ALTER TABLE process_records MODIFY COLUMN source ENUM('voice', 'manual', 'photo', 'import', 'auto') DEFAULT 'manual' COMMENT '记录来源'"))
            db.commit()
            logger.info("✅ 修改source枚举值成功")
        except Exception as e:
            logger.error(f"修改source枚举值失败: {e}")
        
    except Exception as e:
        logger.error(f"❌ 修复枚举值失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始修复枚举值...")
    fix_enum_values()
    logger.info("🎉 枚举值修复完成！")

if __name__ == "__main__":
    main()
