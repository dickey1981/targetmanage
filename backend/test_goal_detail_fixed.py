#!/usr/bin/env python3
"""
测试修复后的目标详情API
"""

import requests
import json

def test_goal_detail_api():
    """测试目标详情API"""
    
    print("🚀 开始测试修复后的目标详情API...")
    
    # 1. 先登录获取token
    print("🔐 测试用户登录...")
    login_data = {
        "wechat_id": "test_user_123",
        "nickname": "测试用户",
        "avatar": "https://example.com/avatar.jpg"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/wechat-login", json=login_data)
        if response.status_code == 200:
            token = response.json()["token"]
            user_id = response.json()["user"]["id"]
            print(f"✅ 登录成功，用户ID: {user_id}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    # 2. 获取目标列表
    print("\n📋 获取目标列表...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get("http://localhost:8000/api/goals/", headers=headers)
        if response.status_code == 200:
            goals = response.json()
            print(f"✅ 获取到 {len(goals)} 个目标")
            if goals:
                goal_id = goals[0]["id"]
                print(f"✅ 第一个目标ID: {goal_id}")
            else:
                print("⚠️ 没有目标，无法测试详情API")
                return
        else:
            print(f"❌ 获取目标列表失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取目标列表失败: {e}")
        return
    
    # 3. 测试获取目标详情
    print(f"\n🔍 测试获取目标详情 (ID: {goal_id})...")
    
    try:
        response = requests.get(f"http://localhost:8000/api/goals/{goal_id}", headers=headers)
        if response.status_code == 200:
            goal_detail = response.json()
            print("✅ 获取目标详情成功")
            print(f"   标题: {goal_detail.get('title', 'N/A')}")
            print(f"   分类: {goal_detail.get('category', 'N/A')}")
            print(f"   描述: {goal_detail.get('description', 'N/A')[:50]}...")
            print(f"   优先级: {goal_detail.get('priority', 'N/A')}")
            print(f"   开始时间: {goal_detail.get('startDate', 'N/A')}")
            print(f"   结束时间: {goal_detail.get('endDate', 'N/A')}")
            print(f"   目标值: {goal_detail.get('targetValue', 'N/A')}")
            print(f"   当前值: {goal_detail.get('currentValue', 'N/A')}")
            print(f"   单位: {goal_detail.get('unit', 'N/A')}")
            print(f"   每日提醒: {goal_detail.get('dailyReminder', 'N/A')}")
            print(f"   截止提醒: {goal_detail.get('deadlineReminder', 'N/A')}")
        else:
            print(f"❌ 获取目标详情失败: {response.status_code}")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 获取目标详情失败: {e}")
    
    # 4. 测试更新目标
    print(f"\n✏️ 测试更新目标...")
    
    update_data = {
        "title": "更新后的目标标题",
        "description": "这是更新后的目标描述",
        "category": "工作",
        "priority": "high",
        "startDate": "2025-01-01",
        "endDate": "2025-12-31",
        "targetValue": "100",
        "currentValue": "30",
        "unit": "小时",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.put(f"http://localhost:8000/api/goals/{goal_id}", 
                              json=update_data, 
                              headers=headers)
        if response.status_code == 200:
            print("✅ 更新目标成功")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 更新目标失败: {response.status_code}")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 更新目标失败: {e}")
    
    # 5. 再次获取目标详情验证更新
    print(f"\n🔍 验证更新后的目标详情...")
    
    try:
        response = requests.get(f"http://localhost:8000/api/goals/{goal_id}", headers=headers)
        if response.status_code == 200:
            goal_detail = response.json()
            print("✅ 验证更新成功")
            print(f"   标题: {goal_detail.get('title', 'N/A')}")
            print(f"   分类: {goal_detail.get('category', 'N/A')}")
            print(f"   描述: {goal_detail.get('description', 'N/A')[:50]}...")
            print(f"   优先级: {goal_detail.get('priority', 'N/A')}")
            print(f"   开始时间: {goal_detail.get('startDate', 'N/A')}")
            print(f"   结束时间: {goal_detail.get('endDate', 'N/A')}")
            print(f"   目标值: {goal_detail.get('targetValue', 'N/A')}")
            print(f"   当前值: {goal_detail.get('currentValue', 'N/A')}")
            print(f"   单位: {goal_detail.get('unit', 'N/A')}")
        else:
            print(f"❌ 验证更新失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 验证更新失败: {e}")
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    test_goal_detail_api()
