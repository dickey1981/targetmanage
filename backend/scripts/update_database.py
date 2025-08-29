#!/usr/bin/env python3
"""
数据库表结构更新脚本
添加缺失的字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def update_database():
    """更新数据库表结构"""
    print("🗄️ 开始更新数据库表结构...")
    
    try:
        with engine.connect() as conn:
            # 检查login_attempts表是否存在wechat_id字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'targetmanage' 
                AND TABLE_NAME = 'login_attempts' 
                AND COLUMN_NAME = 'wechat_id'
            """))
            
            if not result.fetchone():
                print("➕ 添加wechat_id字段到login_attempts表...")
                conn.execute(text("""
                    ALTER TABLE login_attempts 
                    ADD COLUMN wechat_id VARCHAR(100) NULL,
                    ADD INDEX idx_wechat_id (wechat_id)
                """))
                print("✅ wechat_id字段添加成功")
            else:
                print("✅ wechat_id字段已存在")
            
            # 检查login_attempts表是否存在phone_number字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'targetmanage' 
                AND TABLE_NAME = 'login_attempts' 
                AND COLUMN_NAME = 'phone_number'
            """))
            
            if not result.fetchone():
                print("➕ 添加phone_number字段到login_attempts表...")
                conn.execute(text("""
                    ALTER TABLE login_attempts 
                    ADD COLUMN phone_number VARCHAR(20) NULL,
                    ADD INDEX idx_phone_number (phone_number)
                """))
                print("✅ phone_number字段添加成功")
            else:
                print("✅ phone_number字段已存在")
            
            # 检查login_attempts表是否存在failure_reason字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'targetmanage' 
                AND TABLE_NAME = 'login_attempts' 
                AND COLUMN_NAME = 'failure_reason'
            """))
            
            if not result.fetchone():
                print("➕ 添加failure_reason字段到login_attempts表...")
                conn.execute(text("""
                    ALTER TABLE login_attempts 
                    ADD COLUMN failure_reason TEXT NULL
                """))
                print("✅ failure_reason字段添加成功")
            else:
                print("✅ failure_reason字段已存在")
            
            # 检查user_sessions表是否存在is_active字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'targetmanage' 
                AND TABLE_NAME = 'user_sessions' 
                AND COLUMN_NAME = 'is_active'
            """))
            
            if not result.fetchone():
                print("➕ 添加is_active字段到user_sessions表...")
                conn.execute(text("""
                    ALTER TABLE user_sessions 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE
                """))
                print("✅ is_active字段添加成功")
            else:
                print("✅ is_active字段已存在")
            
            # 检查user_sessions表是否存在expires_at字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'targetmanage' 
                AND TABLE_NAME = 'user_sessions' 
                AND COLUMN_NAME = 'expires_at'
            """))
            
            if not result.fetchone():
                print("➕ 添加expires_at字段到user_sessions表...")
                conn.execute(text("""
                    ALTER TABLE user_sessions 
                    ADD COLUMN expires_at DATETIME NULL
                """))
                print("✅ expires_at字段添加成功")
            else:
                print("✅ expires_at字段已存在")
            
            # 检查user_sessions表是否存在updated_at字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'targetmanage' 
                AND TABLE_NAME = 'user_sessions' 
                AND COLUMN_NAME = 'updated_at'
            """))
            
            if not result.fetchone():
                print("➕ 添加updated_at字段到user_sessions表...")
                conn.execute(text("""
                    ALTER TABLE user_sessions 
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """))
                print("✅ updated_at字段添加成功")
            else:
                print("✅ updated_at字段已存在")
            
            conn.commit()
            print("🎉 数据库表结构更新完成！")
            
    except Exception as e:
        print(f"❌ 数据库更新失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🎯 智能目标管理系统 - 数据库更新工具")
    print("=" * 50)
    
    if update_database():
        print("\n✅ 数据库更新成功！")
        print("现在可以重新启动后端服务并测试登录功能。")
    else:
        print("\n❌ 数据库更新失败！")
        print("请检查数据库连接和权限。")

if __name__ == "__main__":
    main()
