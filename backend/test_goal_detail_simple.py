#!/usr/bin/env python3
"""
简单测试目标详情API
"""

import requests

def test_goal_detail_simple():
    """简单测试目标详情API"""
    
    print("🚀 简单测试目标详情API...")
    
    # 1. 登录获取token
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
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
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
                
                # 3. 测试获取目标详情
                print(f"\n🔍 测试获取目标详情...")
                response = requests.get(f"http://localhost:8000/api/goals/{goal_id}", headers=headers)
                
                if response.status_code == 200:
                    goal_detail = response.json()
                    print("✅ 获取目标详情成功")
                    print(f"   标题: {goal_detail.get('title', 'N/A')}")
                    print(f"   分类: {goal_detail.get('category', 'N/A')}")
                    print(f"   描述: {goal_detail.get('description', 'N/A')[:50]}...")
                    print(f"   开始时间: {goal_detail.get('startDate', 'N/A')}")
                    print(f"   结束时间: {goal_detail.get('endDate', 'N/A')}")
                    print(f"   目标值: {goal_detail.get('targetValue', 'N/A')}")
                    print(f"   当前值: {goal_detail.get('currentValue', 'N/A')}")
                    print(f"   单位: {goal_detail.get('unit', 'N/A')}")
                else:
                    print(f"❌ 获取目标详情失败: {response.status_code}")
                    print(f"响应: {response.text}")
            else:
                print("⚠️ 没有目标可测试")
        else:
            print(f"❌ 获取目标列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    test_goal_detail_simple()
