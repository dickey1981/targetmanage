#!/usr/bin/env python3
"""
数据库表结构完整性检查脚本
检查所有表是否包含必要的字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import engine
from sqlalchemy import text

def check_table_schema():
    """检查数据库表结构"""
    print("🔍 开始检查数据库表结构...")
    
    # 定义表结构
    tables_schema = {
        'users': [
            ('id', 'VARCHAR(36)', 'PRIMARY KEY'),
            ('wechat_id', 'VARCHAR(100)', 'UNIQUE NOT NULL'),
            ('nickname', 'VARCHAR(100)', 'NOT NULL'),
            ('avatar', 'TEXT', 'NULL'),
            ('phone_number', 'VARCHAR(20)', 'NULL'),
            ('email', 'VARCHAR(100)', 'NULL'),
            ('notification_enabled', 'BOOLEAN', 'DEFAULT TRUE'),
            ('privacy_level', 'VARCHAR(20)', 'DEFAULT "public"'),
            ('total_goals', 'VARCHAR(10)', 'DEFAULT "0"'),
            ('completed_goals', 'VARCHAR(10)', 'DEFAULT "0"'),
            ('streak_days', 'VARCHAR(10)', 'DEFAULT "0"'),
            ('is_verified', 'BOOLEAN', 'DEFAULT FALSE'),
            ('is_active', 'BOOLEAN', 'DEFAULT TRUE'),
            ('is_locked', 'BOOLEAN', 'DEFAULT FALSE'),
            ('locked_until', 'DATETIME', 'NULL'),
            ('failed_login_attempts', 'VARCHAR(10)', 'DEFAULT "0"'),
            ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
            ('last_login_at', 'DATETIME', 'NULL'),
            ('is_deleted', 'BOOLEAN', 'DEFAULT FALSE'),
            ('deleted_at', 'DATETIME', 'NULL')
        ],
        'user_sessions': [
            ('id', 'VARCHAR(36)', 'PRIMARY KEY'),
            ('user_id', 'VARCHAR(36)', 'NOT NULL'),
            ('session_token', 'VARCHAR(255)', 'UNIQUE NOT NULL'),
            ('refresh_token', 'VARCHAR(255)', 'UNIQUE NOT NULL'),
            ('device_info', 'TEXT', 'NULL'),
            ('ip_address', 'VARCHAR(45)', 'NULL'),
            ('user_agent', 'TEXT', 'NULL'),
            ('is_active', 'BOOLEAN', 'DEFAULT TRUE'),
            ('expires_at', 'DATETIME', 'NOT NULL'),
            ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
        ],
        'login_attempts': [
            ('id', 'VARCHAR(36)', 'PRIMARY KEY'),
            ('user_id', 'VARCHAR(36)', 'NULL'),
            ('wechat_id', 'VARCHAR(100)', 'NULL'),
            ('phone_number', 'VARCHAR(20)', 'NULL'),
            ('ip_address', 'VARCHAR(45)', 'NULL'),
            ('user_agent', 'TEXT', 'NULL'),
            ('success', 'BOOLEAN', 'DEFAULT FALSE'),
            ('failure_reason', 'TEXT', 'NULL'),
            ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP')
        ],
        'user_verifications': [
            ('id', 'VARCHAR(36)', 'PRIMARY KEY'),
            ('user_id', 'VARCHAR(36)', 'NOT NULL'),
            ('verification_type', 'VARCHAR(50)', 'NOT NULL'),
            ('verification_code', 'VARCHAR(10)', 'NOT NULL'),
            ('expires_at', 'DATETIME', 'NOT NULL'),
            ('is_used', 'BOOLEAN', 'DEFAULT FALSE'),
            ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP')
        ]
    }
    
    try:
        with engine.connect() as conn:
            for table_name, expected_columns in tables_schema.items():
                print(f"\n📋 检查表: {table_name}")
                
                # 检查表是否存在
                result = conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'targetmanage' 
                    AND table_name = '{table_name}'
                """))
                
                if result.fetchone()[0] == 0:
                    print(f"❌ 表 {table_name} 不存在")
                    continue
                
                # 检查每个字段
                for column_name, column_type, column_constraints in expected_columns:
                    result = conn.execute(text(f"""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = 'targetmanage' 
                        AND TABLE_NAME = '{table_name}' 
                        AND COLUMN_NAME = '{column_name}'
                    """))
                    
                    column_info = result.fetchone()
                    if column_info:
                        print(f"  ✅ {column_name}: {column_info[1]} ({column_info[2]})")
                    else:
                        print(f"  ❌ {column_name}: 缺失")
                        
                        # 尝试添加缺失字段
                        try:
                            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                            if 'NOT NULL' in column_constraints:
                                sql += " NOT NULL"
                            if 'DEFAULT' in column_constraints:
                                sql += f" {column_constraints}"
                            
                            conn.execute(text(sql))
                            print(f"    ➕ 已添加字段 {column_name}")
                        except Exception as e:
                            print(f"    ❌ 添加字段失败: {e}")
                
                # 检查索引
                result = conn.execute(text(f"""
                    SELECT INDEX_NAME, COLUMN_NAME
                    FROM INFORMATION_SCHEMA.STATISTICS 
                    WHERE TABLE_SCHEMA = 'targetmanage' 
                    AND TABLE_NAME = '{table_name}'
                    ORDER BY INDEX_NAME, SEQ_IN_INDEX
                """))
                
                indexes = result.fetchall()
                if indexes:
                    print(f"  🔗 索引: {', '.join([f'{idx[0]}({idx[1]})' for idx in indexes])}")
                
            conn.commit()
            print("\n🎉 数据库表结构检查完成！")
            
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return False
    
    return True

def main():
    """主函数"""
    print("🎯 智能目标管理系统 - 数据库表结构检查工具")
    print("=" * 60)
    
    if check_table_schema():
        print("\n✅ 数据库表结构检查成功！")
        print("现在可以重新启动后端服务并测试登录功能。")
    else:
        print("\n❌ 数据库表结构检查失败！")
        print("请检查数据库连接和权限。")

if __name__ == "__main__":
    main()
