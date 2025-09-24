#!/usr/bin/env python3
"""
创建测试数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.goal import Goal
from app.models.process_record import ProcessRecord
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

def create_test_data():
    print("🧪 创建测试数据...")
    
    db = SessionLocal()
    try:
        # 查找现有用户
        user = db.query(User).filter(User.wechat_id == "test_user_123").first()
        
        if not user:
            print("❌ 用户不存在")
            return False
        
        print(f"✅ 找到用户: {user.nickname} (ID: {user.id})")
        
        # 创建测试目标
        goal = Goal(
            title="学习Python编程",
            description="掌握Python编程基础，完成一个项目",
            category="study",
            priority="medium",
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            estimated_hours=40.0,
            progress_percentage=25.0,
            is_completed=False,
            is_public=False,
            allow_collaboration=False,
            reminder_enabled=True,
            reminder_frequency="daily",
            user_id=user.id,
            total_tasks=5,
            completed_tasks=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(goal)
        print("✅ 创建目标: 学习Python编程")
        
        # 创建测试记录
        record = ProcessRecord(
            content="完成了第一个Python项目:计算器程序!这是一个重要的里程碑",
            record_type="milestone",
            source="manual",
            is_important=True,
            is_milestone=True,
            is_breakthrough=False,
            tags=["Python", "编程", "项目"],
            goal_id=1,
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(record)
        print("✅ 创建记录: 完成了第一个Python项目")
        
        # 创建另一个目标
        goal2 = Goal(
            title="测试目标:学习Python编程",
            description="这是一个测试目标",
            category="study",
            priority="high",
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=15),
            estimated_hours=20.0,
            progress_percentage=50.0,
            is_completed=False,
            is_public=False,
            allow_collaboration=False,
            reminder_enabled=True,
            reminder_frequency="daily",
            user_id=user.id,
            total_tasks=3,
            completed_tasks=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(goal2)
        print("✅ 创建目标: 测试目标:学习Python编程")
        
        # 创建另一个记录
        record2 = ProcessRecord(
            content="今天学习了Python的基础语法，包括变量、函数和类",
            record_type="process",
            source="manual",
            is_important=False,
            is_milestone=False,
            is_breakthrough=False,
            tags=["Python", "学习", "语法"],
            goal_id=2,
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(record2)
        print("✅ 创建记录: 今天学习了Python的基础语法")
        
        db.commit()
        print("✅ 所有测试数据创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_test_data()
    if success:
        print("\n🎉 测试数据创建完成！")
    else:
        print("\n❌ 测试数据创建失败")
