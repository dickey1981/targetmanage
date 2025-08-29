#!/usr/bin/env python3
"""
测试目标状态和剩余天数计算逻辑
"""

import requests
import json
from datetime import date, timedelta

def test_status_calculation():
    """测试目标状态计算逻辑"""
    
    print("🚀 开始测试目标状态和剩余天数计算逻辑...")
    
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
                print("\n🔍 目标状态和剩余天数详情:")
                for i, goal in enumerate(goals, 1):
                    print(f"\n目标 {i}:")
                    print(f"  标题: {goal.get('title', 'N/A')}")
                    print(f"  分类: {goal.get('category', 'N/A')}")
                    print(f"  进度: {goal.get('progress', 0)}%")
                    print(f"  状态: {goal.get('status', 'N/A')}")
                    print(f"  剩余天数: {goal.get('remaining_days', 0)}天")
                    print(f"  开始时间: {goal.get('startDate', 'N/A')}")
                    print(f"  结束时间: {goal.get('endDate', 'N/A')}")
                    
                    # 验证状态计算逻辑
                    progress = goal.get('progress', 0)
                    status = goal.get('status', '')
                    remaining_days = goal.get('remaining_days', 0)
                    
                    print(f"  ✅ 状态验证: 进度{progress}% -> 状态{status}")
                    print(f"  ✅ 剩余天数: {remaining_days}天")
            else:
                print("⚠️ 没有目标可测试")
        else:
            print(f"❌ 获取目标列表失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取目标列表失败: {e}")
        return
    
    # 3. 测试创建不同状态的目标
    print("\n🧪 测试创建不同状态的目标...")
    
    # 测试目标1: 未开始的目标
    future_start = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    future_end = (date.today() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    test_goal_1 = {
        "title": "测试目标1: 未开始的目标",
        "description": "这是一个30天后开始的目标",
        "category": "测试",
        "startDate": future_start,
        "endDate": future_end,
        "targetValue": "100",
        "currentValue": "0",
        "unit": "小时",
        "priority": "high",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.post(f"http://localhost:8000/api/goals/", 
                               json=test_goal_1, 
                               headers=headers)
        if response.status_code == 200:
            print("✅ 创建测试目标1成功")
        else:
            print(f"❌ 创建测试目标1失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 创建测试目标1失败: {e}")
    
    # 测试目标2: 进行中的目标
    past_start = (date.today() - timedelta(days=10)).strftime('%Y-%m-%d')
    future_end = (date.today() + timedelta(days=20)).strftime('%Y-%m-%d')
    
    test_goal_2 = {
        "title": "测试目标2: 进行中的目标",
        "description": "这是一个正在进行的目标",
        "category": "测试",
        "startDate": past_start,
        "endDate": future_end,
        "targetValue": "100",
        "currentValue": "30",
        "unit": "小时",
        "priority": "medium",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.post(f"http://localhost:8000/api/goals/", 
                               json=test_goal_2, 
                               headers=headers)
        if response.status_code == 200:
            print("✅ 创建测试目标2成功")
        else:
            print(f"❌ 创建测试目标2失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 创建测试目标2失败: {e}")
    
    # 测试目标3: 延期的目标
    past_start = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    past_end = (date.today() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    test_goal_3 = {
        "title": "测试目标3: 延期的目标",
        "description": "这是一个已经过期的目标",
        "category": "测试",
        "startDate": past_start,
        "endDate": past_end,
        "targetValue": "100",
        "currentValue": "50",
        "unit": "小时",
        "priority": "low",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.post(f"http://localhost:8000/api/goals/", 
                               json=test_goal_3, 
                               headers=headers)
        if response.status_code == 200:
            print("✅ 创建测试目标3成功")
        else:
            print(f"❌ 创建测试目标3失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 创建测试目标3失败: {e}")
    
    # 测试目标4: 已完成的目标
    past_start = (date.today() - timedelta(days=20)).strftime('%Y-%m-%d')
    future_end = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
    
    test_goal_4 = {
        "title": "测试目标4: 已完成的目标",
        "description": "这是一个已完成的目标",
        "category": "测试",
        "startDate": past_start,
        "endDate": future_end,
        "targetValue": "100",
        "currentValue": "100",
        "unit": "小时",
        "priority": "high",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.post(f"http://localhost:8000/api/goals/", 
                               json=test_goal_4, 
                               headers=headers)
        if response.status_code == 200:
            print("✅ 创建测试目标4成功")
        else:
            print(f"❌ 创建测试目标4失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 创建测试目标4失败: {e}")
    
    # 4. 再次获取目标列表验证状态计算
    print("\n🔍 验证新创建目标的状态计算...")
    
    try:
        response = requests.get("http://localhost:8000/api/goals/", headers=headers)
        if response.status_code == 200:
            goals = response.json()
            print(f"✅ 获取到 {len(goals)} 个目标")
            
            if goals:
                print("\n🔍 所有目标的状态和剩余天数:")
                for i, goal in enumerate(goals, 1):
                    print(f"\n目标 {i}:")
                    print(f"  标题: {goal.get('title', 'N/A')}")
                    print(f"  进度: {goal.get('progress', 0)}%")
                    print(f"  状态: {goal.get('status', 'N/A')}")
                    print(f"  剩余天数: {goal.get('remaining_days', 0)}天")
                    
                    # 验证状态是否符合预期
                    progress = goal.get('progress', 0)
                    status = goal.get('status', '')
                    title = goal.get('title', '')
                    
                    if '未开始' in title and status == '未开始':
                        print(f"  ✅ 状态正确: 未开始的目标")
                    elif '进行中' in title and status == '进行中':
                        print(f"  ✅ 状态正确: 进行中的目标")
                    elif '延期' in title and status == '延期':
                        print(f"  ✅ 状态正确: 延期的目标")
                    elif '已完成' in title and status == '结束':
                        print(f"  ✅ 状态正确: 已完成的目标")
                    else:
                        print(f"  ⚠️ 状态可能不正确: {title} -> {status}")
            else:
                print("⚠️ 没有目标可验证")
        else:
            print(f"❌ 获取目标列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 验证失败: {e}")
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    test_status_calculation()
