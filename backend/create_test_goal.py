"""
创建测试目标用于拍照记录匹配测试
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

def create_test_goal():
    """创建测试目标"""
    
    # 测试用户ID（替换为你的实际用户ID）
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
        
        # 创建测试目标
        goal_id = str(uuid.uuid4())
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=90)
        
        conn.execute(text("""
            INSERT INTO goals (
                id, user_id, title, description, category, priority, status,
                start_date, end_date, target_value, current_value, unit,
                daily_reminder, deadline_reminder, created_at, updated_at
            ) VALUES (
                :goal_id, :user_id, :title, :description, :category, :priority, :status,
                :start_date, :end_date, :target_value, :current_value, :unit,
                :daily_reminder, :deadline_reminder, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """), {
            "goal_id": goal_id,
            "user_id": user_id,
            "title": "Python学习计划",
            "description": "系统学习Python编程，掌握装饰器、生成器等高级特性",
            "category": "学习",
            "priority": "high",
            "status": "active",
            "start_date": start_date,
            "end_date": end_date,
            "target_value": "100",
            "current_value": "0",
            "unit": "%",
            "daily_reminder": True,
            "deadline_reminder": True
        })
        
        print(f"✅ 创建测试目标成功:")
        print(f"   ID: {goal_id}")
        print(f"   标题: Python学习计划")
        print(f"   类别: 学习")
        print(f"   开始日期: {start_date}")
        print(f"   结束日期: {end_date}")
        print(f"\n📝 提示: 现在可以测试拍照记录功能了！")
        print(f"   拍照内容包含 'Python'、'学习'、'装饰器' 等关键词时会自动关联到这个目标")

if __name__ == "__main__":
    print("🚀 开始创建测试目标...\n")
    create_test_goal()

