"""
创建健身目标用于测试匹配
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import uuid

# 数据库连接
DATABASE_URL = "mysql+pymysql://root:targetM123@sh-cynosdbmysql-grp-hocwbafo.sql.tencentcdb.com:26153/targetmanage"
engine = create_engine(DATABASE_URL)

def create_fitness_goal():
    """创建健身目标"""
    
    # 测试用户ID
    user_id = "537632ba-f2f2-4c80-a0cb-b23318fef17b"
    
    with engine.begin() as conn:
        # 检查用户是否存在
        result = conn.execute(
            text("SELECT id, nickname FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        user = result.fetchone()
        
        if not user:
            print(f"❌ 用户不存在: {user_id}")
            return
        
        print(f"✅ 找到用户: {user[1]}")
        
        # 创建健身目标
        goal_id = str(uuid.uuid4())
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30)
        
        conn.execute(text("""
            INSERT INTO goals (
                id, user_id, title, description, category, priority, status,
                start_date, end_date, target_date, target_value, current_value, unit,
                daily_reminder, deadline_reminder, created_at, updated_at
            ) VALUES (
                :goal_id, :user_id, :title, :description, :category, :priority, :status,
                :start_date, :end_date, :target_date, :target_value, :current_value, :unit,
                :daily_reminder, :deadline_reminder, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """), {
            "goal_id": goal_id,
            "user_id": user_id,
            "title": "每月跑步100公里",
            "description": "坚持每月跑步100公里，提升身体素质",
            "category": "健身",
            "priority": "high",
            "status": "active",
            "start_date": start_date,
            "end_date": end_date,
            "target_date": end_date,
            "target_value": "100",
            "current_value": "0",
            "unit": "公里",
            "daily_reminder": True,
            "deadline_reminder": True
        })
        
        print(f"✅ 创建健身目标成功:")
        print(f"   ID: {goal_id}")
        print(f"   标题: 每月跑步100公里")
        print(f"   类别: 健身")
        print(f"   单位: 公里")
        print(f"   开始日期: {start_date}")
        print(f"   结束日期: {end_date}")
        print(f"\n📝 提示: 现在'跑步'相关记录会正确匹配到这个目标！")

if __name__ == "__main__":
    print("🚀 开始创建健身目标...\n")
    create_fitness_goal()

