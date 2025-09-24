#!/usr/bin/env python3
"""
测试目标-记录关联和进度更新功能
Test goal-record association and progress update functionality
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.goal import Goal
from app.models.process_record import ProcessRecord, ProcessRecordType, ProcessRecordSource
from app.services.goal_progress_service import GoalProgressService
from sqlalchemy.orm import Session

# 配置
BASE_URL = "http://127.0.0.1:8000"
USER_ID = "537632ba-f2f2-4c80-a0cb-b23318fef17b"

def test_goal_record_integration():
    """测试目标-记录关联和进度更新"""
    print("🧪 开始测试目标-记录关联和进度更新功能")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 1. 创建一个测试目标（使用原生SQL）
        print("\n1️⃣ 创建测试目标...")
        goal_id = str(uuid.uuid4())
        
        # 使用原生SQL插入目标
        from sqlalchemy import text
        db.execute(text("""
            INSERT INTO goals (id, title, description, category, priority, status, 
                              start_date, end_date, target_value, current_value, unit, user_id, created_at, updated_at)
            VALUES (:goal_id, :title, :description, :category, :priority, :status,
                    :start_date, :end_date, :target_value, :current_value, :unit, :user_id, NOW(), NOW())
        """), {
            "goal_id": goal_id,
            "title": "测试目标：学习Python编程",
            "description": "在3个月内掌握Python基础编程",
            "category": "study",
            "priority": "high",
            "status": "active",
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=90)).date(),
            "target_value": "100",
            "current_value": "0",
            "unit": "章节",
            "user_id": USER_ID
        })
        
        db.commit()
        
        print(f"✅ 目标创建成功: {goal_id}")
        print(f"   标题: 测试目标：学习Python编程")
        print(f"   初始进度: 0.0%")
    
        # 2. 创建过程记录（不关联目标）
        print("\n2️⃣ 创建过程记录（不关联目标）...")
        record_1 = ProcessRecord(
            content="今天开始学习Python基础语法，感觉很有趣",
            record_type=ProcessRecordType.process,
            source=ProcessRecordSource.manual,
            user_id=USER_ID
            # 注意：没有goal_id
        )
        
        db.add(record_1)
        db.commit()
        db.refresh(record_1)
        
        print(f"✅ 过程记录创建成功: {record_1.id}")
        print(f"   内容: {record_1.content[:30]}...")
        
        # 3. 创建进度记录（关联目标）
        print("\n3️⃣ 创建进度记录（关联目标）...")
        record_2 = ProcessRecord(
            content="完成了Python基础语法的学习，进度达到30%",
            record_type=ProcessRecordType.progress,
            source=ProcessRecordSource.manual,
            goal_id=goal_id,
            user_id=USER_ID
        )
        
        db.add(record_2)
        db.commit()
        db.refresh(record_2)
        
        print(f"✅ 进度记录创建成功: {record_2.id}")
        print(f"   内容: {record_2.content[:30]}...")
        
        # 4. 使用进度服务更新目标进度
        print("\n4️⃣ 更新目标进度...")
        progress_service = GoalProgressService(db)
        progress_updated = progress_service.update_goal_progress_from_record(goal_id, record_2)
        
        if progress_updated:
            # 重新查询目标
            result = db.execute(text("SELECT current_value, target_value, status FROM goals WHERE id = :goal_id"), {
                "goal_id": goal_id
            })
            goal_data = result.fetchone()
            current_value = float(goal_data[0]) if goal_data[0] else 0
            target_value = float(goal_data[1]) if goal_data[1] else 100
            progress = (current_value / target_value * 100) if target_value > 0 else 0
            print(f"✅ 目标进度更新成功")
            print(f"   当前值: {current_value}/{target_value}")
            print(f"   进度: {progress:.1f}%")
            print(f"   状态: {goal_data[2]}")
        else:
            print(f"❌ 目标进度更新失败")
        
        # 5. 创建里程碑记录
        print("\n5️⃣ 创建里程碑记录...")
        record_3 = ProcessRecord(
            content="完成了第一个Python项目：计算器程序！这是一个重要的里程碑",
            record_type=ProcessRecordType.milestone,
            source=ProcessRecordSource.manual,
            goal_id=goal_id,
            user_id=USER_ID,
            is_milestone=True
        )
        
        db.add(record_3)
        db.commit()
        db.refresh(record_3)
        
        print(f"✅ 里程碑记录创建成功: {record_3.id}")
        print(f"   内容: {record_3.content[:30]}...")
        
        # 6. 再次更新目标进度
        print("\n6️⃣ 再次更新目标进度...")
        progress_updated_2 = progress_service.update_goal_progress_from_record(goal_id, record_3)
        
        if progress_updated_2:
            # 重新查询目标
            result = db.execute(text("SELECT current_value, target_value, status FROM goals WHERE id = :goal_id"), {
                "goal_id": goal_id
            })
            goal_data = result.fetchone()
            current_value = float(goal_data[0]) if goal_data[0] else 0
            target_value = float(goal_data[1]) if goal_data[1] else 100
            progress = (current_value / target_value * 100) if target_value > 0 else 0
            print(f"✅ 目标进度再次更新成功")
            print(f"   当前值: {current_value}/{target_value}")
            print(f"   进度: {progress:.1f}%")
            print(f"   状态: {goal_data[2]}")
        else:
            print(f"❌ 目标进度再次更新失败")
        
        # 7. 获取目标进度摘要
        print("\n7️⃣ 获取目标进度摘要...")
        summary = progress_service.get_goal_progress_summary(goal_id)
        
        if summary:
            print(f"✅ 目标进度摘要获取成功")
            print(f"   目标ID: {summary['goal_id']}")
            print(f"   当前进度: {summary['current_progress']}%")
            print(f"   总记录数: {summary['total_records']}")
            print(f"   里程碑数: {summary['milestone_count']}")
            print(f"   突破数: {summary['breakthrough_count']}")
            print(f"   记录类型分布: {summary['records_by_type']}")
        else:
            print(f"❌ 目标进度摘要获取失败")
        
        # 8. 获取目标相关记录
        print("\n8️⃣ 获取目标相关记录...")
        related_records = db.query(ProcessRecord).filter(
            ProcessRecord.goal_id == goal_id
        ).all()
        
        print(f"✅ 目标相关记录获取成功")
        print(f"   总记录数: {len(related_records)}")
        for record in related_records:
            print(f"   - {record.record_type.value}: {record.content[:30]}...")
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_goal_record_integration()
