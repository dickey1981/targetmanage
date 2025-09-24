#!/usr/bin/env python3
"""
直接创建token用于测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.auth_service import AuthService
from app.database import SessionLocal
from app.models.user import User
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

def create_direct_token():
    print("🧪 直接创建token...")
    
    db = SessionLocal()
    try:
        # 查找现有用户
        user = db.query(User).filter(User.wechat_id == "test_user_123").first()
        
        if not user:
            print("❌ 用户不存在，请先运行创建测试数据")
            return None
        
        print(f"✅ 找到用户: {user.nickname} (ID: {user.id})")
        
        # 创建认证服务
        auth_service = AuthService(db)
        
        # 创建模拟请求对象
        class MockRequest:
            def __init__(self):
                self.client = type('Client', (), {'host': '127.0.0.1'})()
                self.headers = {}
        
        mock_request = MockRequest()
        
        # 创建用户会话和token
        session = auth_service.create_user_session(user.id, mock_request)
        
        print(f"✅ 创建会话成功")
        print(f"Session ID: {session.id}")
        print(f"Session Token: {session.session_token[:50]}...")
        print(f"Refresh Token: {session.refresh_token[:50]}...")
        
        return session.session_token
        
    except Exception as e:
        print(f"❌ 创建token失败: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    token = create_direct_token()
    if token:
        print(f"\n🎉 成功获取token: {token}")
        
        # 测试token
        print("\n🧪 测试token...")
        import requests
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试目标列表
        goals_response = requests.get("http://localhost:8000/api/goals/", headers=headers, params={"status": "active", "page": 1, "page_size": 50})
        print(f"目标列表响应: {goals_response.status_code}")
        if goals_response.status_code == 200:
            goals_data = goals_response.json()
            print(f"✅ 获取到 {len(goals_data.get('goals', []))} 个目标")
        else:
            print(f"❌ 目标列表请求失败: {goals_response.text}")
        
        # 测试记录列表
        records_response = requests.get("http://localhost:8000/api/process-records/", headers=headers, params={"page": 1, "page_size": 10})
        print(f"记录列表响应: {records_response.status_code}")
        if records_response.status_code == 200:
            records_data = records_response.json()
            print(f"✅ 获取到 {len(records_data.get('records', []))} 条记录")
        else:
            print(f"❌ 记录列表请求失败: {records_response.text}")
    else:
        print("\n❌ 获取token失败")
