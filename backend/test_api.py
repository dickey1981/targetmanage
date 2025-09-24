#!/usr/bin/env python3
"""
测试API端点
"""
import requests

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    print("🚀 测试API端点...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ 健康检查: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ 根路径: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径失败: {e}")
    
    # 测试目标API（不需要认证）
    try:
        response = requests.get(f"{base_url}/api/goals/today")
        print(f"✅ 今日目标API: {response.status_code}")
        if response.status_code == 401:
            print("   需要认证（这是正常的）")
        elif response.status_code == 200:
            print("   返回数据成功")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 今日目标API失败: {e}")
    
    # 测试API文档
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ API文档: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档失败: {e}")

if __name__ == "__main__":
    test_api_endpoints()
