#!/usr/bin/env python3
"""
使用SQL直接插入测试数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta

def insert_test_data_sql():
    print("🧪 使用SQL插入测试数据...")
    
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
        
        # 插入目标1
        print("📝 插入目标1...")
        db.execute(text("""
            INSERT INTO goals (title, description, category, priority, status, 
                              start_date, end_date, estimated_hours, progress_percentage, 
                              is_completed, is_public, allow_collaboration, reminder_enabled, 
                              reminder_frequency, user_id, total_tasks, completed_tasks, 
                              created_at, updated_at)
            VALUES (:title, :description, :category, :priority, :status,
                    :start_date, :end_date, :estimated_hours, :progress_percentage,
                    :is_completed, :is_public, :allow_collaboration, :reminder_enabled,
                    :reminder_frequency, :user_id, :total_tasks, :completed_tasks,
                    :created_at, :updated_at)
        """), {
            "title": "学习Python编程",
            "description": "掌握Python编程基础，完成一个项目",
            "category": "study",
            "priority": "medium",
            "status": "active",
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=30),
            "estimated_hours": 40.0,
            "progress_percentage": 25.0,
            "is_completed": False,
            "is_public": False,
            "allow_collaboration": False,
            "reminder_enabled": True,
            "reminder_frequency": "daily",
            "user_id": user_id,
            "total_tasks": 5,
            "completed_tasks": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # 获取刚插入的目标ID
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        goal1_id = result.fetchone()[0]
        print(f"✅ 目标1创建成功，ID: {goal1_id}")
        
        # 插入目标2
        print("📝 插入目标2...")
        db.execute(text("""
            INSERT INTO goals (title, description, category, priority, status, 
                              start_date, end_date, estimated_hours, progress_percentage, 
                              is_completed, is_public, allow_collaboration, reminder_enabled, 
                              reminder_frequency, user_id, total_tasks, completed_tasks, 
                              created_at, updated_at)
            VALUES (:title, :description, :category, :priority, :status,
                    :start_date, :end_date, :estimated_hours, :progress_percentage,
                    :is_completed, :is_public, :allow_collaboration, :reminder_enabled,
                    :reminder_frequency, :user_id, :total_tasks, :completed_tasks,
                    :created_at, :updated_at)
        """), {
            "title": "测试目标:学习Python编程",
            "description": "这是一个测试目标",
            "category": "study",
            "priority": "high",
            "status": "active",
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=15),
            "estimated_hours": 20.0,
            "progress_percentage": 50.0,
            "is_completed": False,
            "is_public": False,
            "allow_collaboration": False,
            "reminder_enabled": True,
            "reminder_frequency": "daily",
            "user_id": user_id,
            "total_tasks": 3,
            "completed_tasks": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # 获取刚插入的目标ID
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        goal2_id = result.fetchone()[0]
        print(f"✅ 目标2创建成功，ID: {goal2_id}")
        
        # 插入记录1
        print("📝 插入记录1...")
        db.execute(text("""
            INSERT INTO process_records (content, record_type, source, is_important, 
                                        is_milestone, is_breakthrough, tags, goal_id, 
                                        user_id, created_at, updated_at)
            VALUES (:content, :record_type, :source, :is_important,
                    :is_milestone, :is_breakthrough, :tags, :goal_id,
                    :user_id, :created_at, :updated_at)
        """), {
            "content": "完成了第一个Python项目:计算器程序!这是一个重要的里程碑",
            "record_type": "milestone",
            "source": "manual",
            "is_important": True,
            "is_milestone": True,
            "is_breakthrough": False,
            "tags": '["Python", "编程", "项目"]',
            "goal_id": goal1_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # 获取刚插入的记录ID
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        record1_id = result.fetchone()[0]
        print(f"✅ 记录1创建成功，ID: {record1_id}，关联目标ID: {goal1_id}")
        
        # 插入记录2
        print("📝 插入记录2...")
        db.execute(text("""
            INSERT INTO process_records (content, record_type, source, is_important, 
                                        is_milestone, is_breakthrough, tags, goal_id, 
                                        user_id, created_at, updated_at)
            VALUES (:content, :record_type, :source, :is_important,
                    :is_milestone, :is_breakthrough, :tags, :goal_id,
                    :user_id, :created_at, :updated_at)
        """), {
            "content": "今天学习了Python的基础语法，包括变量、函数和类",
            "record_type": "process",
            "source": "manual",
            "is_important": False,
            "is_milestone": False,
            "is_breakthrough": False,
            "tags": '["Python", "学习", "语法"]',
            "goal_id": goal2_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # 获取刚插入的记录ID
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        record2_id = result.fetchone()[0]
        print(f"✅ 记录2创建成功，ID: {record2_id}，关联目标ID: {goal2_id}")
        
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
    success = insert_test_data_sql()
    if success:
        print("\n🎉 测试数据插入完成！")
    else:
        print("\n❌ 测试数据插入失败")
