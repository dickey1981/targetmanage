#!/usr/bin/env python3
"""
测试目标详情API - 简化版本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_goal_detail_api():
    """测试目标详情API"""
    
    print("🚀 开始测试目标详情API...")
    print(f"测试地址: {BASE_URL}")
    
    # 1. 先登录获取token
    print("🔐 测试用户登录...")
    login_data = {
        "wechat_id": "test_user_123",
        "nickname": "测试用户",
        "avatar": "https://example.com/avatar.jpg"
    }
    
    try:
        print(f"发送登录请求到: {BASE_URL}/api/auth/wechat-login")
        response = requests.post(f"{BASE_URL}/api/auth/wechat-login", json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json()["token"]
            user_id = response.json()["user"]["id"]
            print(f"✅ 登录成功，用户ID: {user_id}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    # 2. 获取目标列表
    print("\n📋 获取目标列表...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"发送请求到: {BASE_URL}/api/goals/")
        response = requests.get(f"{BASE_URL}/api/goals/", headers=headers)
        print(f"获取目标列表响应状态码: {response.status_code}")
        
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
            print(f"响应内容: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取目标列表失败: {e}")
        return
    
    # 3. 测试获取目标详情
    print(f"\n🔍 测试获取目标详情 (ID: {goal_id})...")
    
    try:
        print(f"发送请求到: {BASE_URL}/api/goals/{goal_id}")
        response = requests.get(f"{BASE_URL}/api/goals/{goal_id}", headers=headers)
        print(f"获取目标详情响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            goal_detail = response.json()
            print("✅ 获取目标详情成功")
            print(f"   标题: {goal_detail.get('title', 'N/A')}")
            print(f"   分类: {goal_detail.get('category', 'N/A')}")
            print(f"   描述: {goal_detail.get('description', 'N/A')[:50]}...")
        else:
            print(f"❌ 获取目标详情失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 获取目标详情失败: {e}")
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    print("开始执行测试脚本...")
    test_goal_detail_api()
    print("测试脚本执行完毕！")
