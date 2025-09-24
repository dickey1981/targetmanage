#!/usr/bin/env python3
"""
用户认证集成测试脚本
测试微信登录、用户创建、会话管理等功能
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
TEST_CODE = "test_code_123456"
TEST_USER_INFO = {
    "nickName": "测试用户",
    "avatarUrl": "https://example.com/avatar.jpg",
    "gender": 1,
    "country": "中国",
    "province": "北京",
    "city": "北京",
    "language": "zh_CN"
}

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_create_tables():
    """测试创建数据库表"""
    print("🔨 测试创建数据库表...")
    try:
        response = requests.get(f"{BASE_URL}/api/test/create-tables")
        if response.status_code == 200:
            print("✅ 数据库表创建成功")
            return True
        else:
            print(f"❌ 数据库表创建失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 数据库表创建异常: {e}")
        return False

def test_wechat_login():
    """测试微信登录接口"""
    print("🔐 测试微信登录接口...")
    try:
        data = {
            "code": TEST_CODE,
            "userInfo": TEST_USER_INFO,
            "phoneNumber": "13800138000"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/wechat-login",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 微信登录成功")
                print(f"用户信息: {result.get('data', {}).get('user', {})}")
                return result.get("data", {}).get("token")
            else:
                print(f"❌ 微信登录失败: {result.get('message')}")
                return None
        else:
            print(f"❌ 微信登录请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 微信登录异常: {e}")
        return None

def test_token_validation(token):
    """测试token验证"""
    if not token:
        print("❌ 没有token，跳过验证测试")
        return False
        
    print("🔍 测试token验证...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/validate", headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Token验证成功")
                return True
            else:
                print(f"❌ Token验证失败: {result.get('message')}")
                return False
        else:
            print(f"❌ Token验证请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Token验证异常: {e}")
        return False

def test_get_user_info(token):
    """测试获取用户信息"""
    if not token:
        print("❌ 没有token，跳过用户信息测试")
        return False
        
    print("👤 测试获取用户信息...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 获取用户信息成功")
            return True
        else:
            print(f"❌ 获取用户信息失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return False

def test_goals_api(token):
    """测试目标相关API"""
    if not token:
        print("❌ 没有token，跳过目标API测试")
        return False
        
    print("🎯 测试目标API...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/goals/", headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 目标API测试成功")
            return True
        else:
            print(f"❌ 目标API测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 目标API测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始用户认证集成测试")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health_check():
        print("❌ 服务不可用，测试终止")
        return
    
    # 2. 创建数据库表
    if not test_create_tables():
        print("❌ 数据库表创建失败，测试终止")
        return
    
    # 3. 微信登录测试
    token = test_wechat_login()
    
    # 4. Token验证测试
    test_token_validation(token)
    
    # 5. 获取用户信息测试
    test_get_user_info(token)
    
    # 6. 目标API测试
    test_goals_api(token)
    
    print("=" * 50)
    print("🎉 用户认证集成测试完成")

if __name__ == "__main__":
    main()
