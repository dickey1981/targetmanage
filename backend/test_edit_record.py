#!/usr/bin/env python3
"""
测试编辑记录功能的API
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
PASSWORD = "testpass123"

def test_edit_record():
    print("🧪 测试编辑记录功能...")
    
    # 1. 使用微信登录测试接口
    print("\n1️⃣ 微信登录测试...")
    login_data = {
        "code": "test_code_123",
        "userInfo": {
            "nickName": "测试用户",
            "avatarUrl": "https://example.com/avatar.jpg"
        }
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/wechat-login", json=login_data)
    print(f"登录响应状态: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return
    
    login_data = login_response.json()
    if login_data.get("success"):
        token = login_data["data"]["token"]
        print(f"✅ 登录成功，获取到token: {token[:20]}...")
    else:
        print(f"❌ 登录失败: {login_data.get('message')}")
        return
    
    # 2. 获取目标列表
    print("\n2️⃣ 获取目标列表...")
    goals_headers = {"Authorization": f"Bearer {token}"}
    goals_response = requests.get(f"{BASE_URL}/api/goals/", headers=goals_headers, params={"status": "active", "page": 1, "page_size": 50})
    print(f"目标列表响应状态: {goals_response.status_code}")
    
    if goals_response.status_code == 200:
        goals_data = goals_response.json()
        goals = goals_data.get("goals", [])
        print(f"✅ 获取到 {len(goals)} 个目标")
        for goal in goals:
            print(f"  - ID: {goal['id']}, 标题: {goal['title']}, 分类: {goal.get('category', 'N/A')}")
    else:
        print(f"❌ 获取目标列表失败: {goals_response.text}")
    
    # 3. 获取记录列表
    print("\n3️⃣ 获取记录列表...")
    records_response = requests.get(f"{BASE_URL}/api/process-records/", headers=goals_headers, params={"page": 1, "page_size": 10})
    print(f"记录列表响应状态: {records_response.status_code}")
    
    if records_response.status_code == 200:
        records_data = records_response.json()
        records = records_data.get("records", [])
        print(f"✅ 获取到 {len(records)} 条记录")
        
        if records:
            # 选择第一条记录进行编辑测试
            record = records[0]
            record_id = record["id"]
            print(f"📝 选择记录进行编辑测试: ID={record_id}, 内容={record['content'][:50]}...")
            
            # 4. 获取记录详情
            print(f"\n4️⃣ 获取记录详情 (ID: {record_id})...")
            detail_response = requests.get(f"{BASE_URL}/api/process-records/{record_id}", headers=goals_headers)
            print(f"记录详情响应状态: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f"✅ 记录详情获取成功")
                print(f"  - 内容: {detail_data['content']}")
                print(f"  - 目标ID: {detail_data.get('goal_id')}")
                print(f"  - 记录类型: {detail_data.get('record_type')}")
                print(f"  - 重要标记: 重要={detail_data.get('is_important')}, 里程碑={detail_data.get('is_milestone')}, 突破={detail_data.get('is_breakthrough')}")
                print(f"  - 标签: {detail_data.get('tags', [])}")
            else:
                print(f"❌ 获取记录详情失败: {detail_response.text}")
        else:
            print("⚠️ 没有记录可供测试")
    else:
        print(f"❌ 获取记录列表失败: {records_response.text}")

if __name__ == "__main__":
    test_edit_record()
