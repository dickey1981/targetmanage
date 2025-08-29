#!/usr/bin/env python3
"""
测试goals表结构的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

def test_table_structure():
    """测试goals表结构"""
    try:
        # 直接使用数据库连接字符串
        database_url = "mysql+pymysql://root:targetM123@sh-cynosdbmysql-grp-hocwbafo.sql.tencentcdb.com:26153/targetmanage"
        
        print(f"🔗 连接到数据库: {database_url.split('@')[1]}")
        
        # 创建数据库连接
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # 检查goals表是否存在
            result = connection.execute(text("SHOW TABLES LIKE 'goals'"))
            if not result.fetchone():
                print("❌ goals表不存在")
                return False
            
            print("✅ goals表存在")
            
            # 检查表结构
            result = connection.execute(text("DESCRIBE goals"))
            columns = result.fetchall()
            
            print(f"📋 goals表结构 ({len(columns)} 列):")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
            
            required_columns = [
                'id', 'title', 'description', 'category', 'priority', 'status',
                'start_date', 'end_date', 'target_date', 'target_value', 'current_value', 'unit',
                'daily_reminder', 'deadline_reminder', 'user_id', 'created_at', 'updated_at'
            ]
            
            existing_columns = [col[0] for col in columns]
            print(f"\n现有列: {existing_columns}")
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            if missing_columns:
                print(f"❌ 缺少的列: {missing_columns}")
                return False
            else:
                print("✅ 所有必需的列都存在")
                return True
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔍 开始测试goals表结构...")
    success = test_table_structure()
    if success:
        print("🎉 表结构测试通过！")
    else:
        print("❌ 表结构测试失败！")
