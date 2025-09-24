#!/usr/bin/env python3
"""
使用简化的SQL插入测试数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta

def simple_insert_data():
    print("🧪 使用简化SQL插入测试数据...")
    
    db = SessionLocal()
    try:
        # 查找用户ID
        result = db.execute(text("SELECT id FROM users WHERE wechat_id = 'test_user_123'"))
        user_row = result.fetchone()
        
        if not user_row:
            print("❌ 用户不存在")
            return False
        
        user_id = user_row[0]
        print(f"✅ 找到用户ID: {user_id}")
        
        # 清理现有数据
        print("🗑️ 清理现有数据...")
        db.execute(text("DELETE FROM process_records WHERE user_id = :user_id"), {"user_id": user_id})
        db.execute(text("DELETE FROM goals WHERE user_id = :user_id"), {"user_id": user_id})
        
        # 插入目标1 - 只使用基本字段
        print("📝 插入目标1...")
        db.execute(text("""
            INSERT INTO goals (id, title, description, category, priority, status, 
                              user_id, created_at, updated_at)
            VALUES (:id, :title, :description, :category, :priority, :status,
                    :user_id, :created_at, :updated_at)
        """), {
            "id": "goal_1",
            "title": "学习Python编程",
            "description": "掌握Python编程基础，完成一个项目",
            "category": "study",
            "priority": "medium",
            "status": "active",
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        print(f"✅ 目标1创建成功，ID: goal_1")
        
        # 插入目标2
        print("📝 插入目标2...")
        db.execute(text("""
            INSERT INTO goals (id, title, description, category, priority, status, 
                              user_id, created_at, updated_at)
            VALUES (:id, :title, :description, :category, :priority, :status,
                    :user_id, :created_at, :updated_at)
        """), {
            "id": "goal_2",
            "title": "测试目标:学习Python编程",
            "description": "这是一个测试目标",
            "category": "study",
            "priority": "high",
            "status": "active",
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        print(f"✅ 目标2创建成功，ID: goal_2")
        
        # 插入记录1
        print("📝 插入记录1...")
        db.execute(text("""
            INSERT INTO process_records (id, content, record_type, source, is_important, 
                                        is_milestone, is_breakthrough, goal_id, 
                                        user_id, created_at, updated_at)
            VALUES (:id, :content, :record_type, :source, :is_important,
                    :is_milestone, :is_breakthrough, :goal_id,
                    :user_id, :created_at, :updated_at)
        """), {
            "id": "record_1",
            "content": "完成了第一个Python项目:计算器程序!这是一个重要的里程碑",
            "record_type": "milestone",
            "source": "manual",
            "is_important": True,
            "is_milestone": True,
            "is_breakthrough": False,
            "goal_id": "goal_1",
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        print(f"✅ 记录1创建成功，ID: record_1，关联目标ID: goal_1")
        
        # 插入记录2
        print("📝 插入记录2...")
        db.execute(text("""
            INSERT INTO process_records (id, content, record_type, source, is_important, 
                                        is_milestone, is_breakthrough, goal_id, 
                                        user_id, created_at, updated_at)
            VALUES (:id, :content, :record_type, :source, :is_important,
                    :is_milestone, :is_breakthrough, :goal_id,
                    :user_id, :created_at, :updated_at)
        """), {
            "id": "record_2",
            "content": "今天学习了Python的基础语法，包括变量、函数和类",
            "record_type": "process",
            "source": "manual",
            "is_important": False,
            "is_milestone": False,
            "is_breakthrough": False,
            "goal_id": "goal_2",
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        print(f"✅ 记录2创建成功，ID: record_2，关联目标ID: goal_2")
        
        db.commit()
        print("✅ 所有测试数据插入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 插入测试数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = simple_insert_data()
    if success:
        print("\n🎉 测试数据插入完成！")
    else:
        print("\n❌ 测试数据插入失败")
