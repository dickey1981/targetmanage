#!/usr/bin/env python3
"""
重新创建过程记录表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_process_records_table():
    """重新创建过程记录表"""
    try:
        db = next(get_db())
        
        # 删除现有表
        try:
            db.execute(text("DROP TABLE IF EXISTS process_records"))
            db.commit()
            logger.info("✅ 删除现有表成功")
        except Exception as e:
            logger.error(f"删除现有表失败: {e}")
        
        # 创建新的过程记录表
        create_table_sql = """
        CREATE TABLE process_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) COMMENT '记录标题',
            content TEXT NOT NULL COMMENT '记录内容',
            record_type ENUM('progress', 'process', 'milestone', 'difficulty', 'method', 'reflection', 'adjustment', 'achievement', 'insight', 'other') DEFAULT 'process' COMMENT '记录类型',
            source ENUM('voice', 'manual', 'photo', 'import', 'auto') DEFAULT 'manual' COMMENT '记录来源',
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
            event_date DATETIME COMMENT '事件发生时间',
            mood VARCHAR(20) COMMENT '心情状态',
            energy_level INT COMMENT '精力水平：1-10',
            difficulty_level INT COMMENT '困难程度：1-10',
            tags JSON COMMENT '标签列表',
            keywords JSON COMMENT '关键词列表',
            sentiment VARCHAR(20) COMMENT '情感分析',
            is_important BOOLEAN DEFAULT FALSE COMMENT '是否重要',
            is_milestone BOOLEAN DEFAULT FALSE COMMENT '是否里程碑',
            is_breakthrough BOOLEAN DEFAULT FALSE COMMENT '是否突破',
            attachments JSON COMMENT '附件信息',
            location VARCHAR(200) COMMENT '记录地点',
            weather VARCHAR(50) COMMENT '天气情况',
            source_data JSON COMMENT '源数据详情',
            confidence_score INT COMMENT '置信度分数：0-100',
            user_id INT NOT NULL COMMENT '用户ID',
            goal_id INT COMMENT '目标ID',
            parent_record_id INT COMMENT '父记录ID',
            like_count INT DEFAULT 0 COMMENT '点赞数',
            comment_count INT DEFAULT 0 COMMENT '评论数',
            view_count INT DEFAULT 0 COMMENT '查看数',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
            INDEX idx_user_id (user_id),
            INDEX idx_goal_id (goal_id),
            INDEX idx_record_type (record_type),
            INDEX idx_recorded_at (recorded_at),
            INDEX idx_is_important (is_important),
            INDEX idx_is_milestone (is_milestone)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='过程记录表';
        """
        
        db.execute(text(create_table_sql))
        db.commit()
        
        logger.info("✅ process_records表创建成功")
        
        # 检查表结构
        result = db.execute(text("DESCRIBE process_records"))
        columns = result.fetchall()
        logger.info("新表结构:")
        for column in columns:
            logger.info(f"  {column[0]} - {column[1]} - {column[2]}")
        
    except Exception as e:
        logger.error(f"❌ 重新创建表失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始重新创建过程记录表...")
    recreate_process_records_table()
    logger.info("🎉 表重新创建完成！")

if __name__ == "__main__":
    main()
