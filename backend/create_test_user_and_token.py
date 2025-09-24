#!/usr/bin/env python3
"""
创建测试用户和token
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"

def create_test_user_and_token():
    print("🧪 创建测试用户和token...")
    
    # 1. 创建测试数据
    print("\n1️⃣ 创建测试数据...")
    create_response = requests.post(f"{BASE_URL}/api/test/create-test-data")
    print(f"创建测试数据响应状态: {create_response.status_code}")
    
    if create_response.status_code == 200:
        data = create_response.json()
        print(f"✅ 测试数据创建成功: {data}")
    else:
        print(f"❌ 创建测试数据失败: {create_response.text}")
        return None
    
    # 2. 使用微信登录测试接口
    print("\n2️⃣ 微信登录测试...")
    login_data = {
        "code": "test_code_123",
        "userInfo": {
            "nickName": "测试用户",
            "avatarUrl": "https://example.com/avatar.jpg"
        }
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/wechat-login", json=login_data)
    print(f"登录响应状态: {login_response.status_code}")
    print(f"登录响应内容: {login_response.text}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        if login_data.get("success"):
            token = login_data["data"]["token"]
            print(f"✅ 登录成功，获取到token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {login_data.get('message')}")
    else:
        print(f"❌ 登录请求失败: {login_response.text}")
    
    return None

if __name__ == "__main__":
    token = create_test_user_and_token()
    if token:
        print(f"\n🎉 成功获取token: {token}")
    else:
        print("\n❌ 获取token失败")
