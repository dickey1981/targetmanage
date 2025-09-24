#!/usr/bin/env python3
"""
测试目标创建API
"""

import requests
import json

def test_goal_creation():
    """测试目标创建API"""
    print("🔍 测试目标创建API...")
    
    base_url = "http://localhost:8000"
    
    # 测试数据
    test_goal_data = {
        "title": "我要在3个月内减重10斤",
        "category": "健康",
        "description": "通过我要在3个月内减重10斤实现目标：10斤",
        "startDate": "2025-09-02T09:48:47.991844",
        "endDate": "2025-12-01T09:48:47.991844",
        "targetValue": "10",
        "currentValue": "0",
        "unit": "斤",
        "priority": "medium",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        # 测试目标创建API
        response = requests.post(
            f"{base_url}/api/goals/",
            json=test_goal_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token"  # 测试用的token
            },
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 目标创建成功")
                print(f"   创建的目标ID: {data.get('data', {}).get('id', 'N/A')}")
                return True
            else:
                print(f"❌ 目标创建失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_voice_parsing():
    """测试语音解析API"""
    print("\n🔍 测试语音解析API...")
    
    base_url = "http://localhost:8000"
    test_voice_text = "我要在3个月内减重10斤"
    
    try:
        response = requests.post(
            f"{base_url}/api/goals/test-parse-voice",
            json={"voice_text": test_voice_text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                parsed_data = data.get('data', {})
                validation = data.get('validation', {})
                
                print("✅ 语音解析成功")
                print(f"   标题: {parsed_data.get('title', 'N/A')}")
                print(f"   类别: {parsed_data.get('category', 'N/A')}")
                print(f"   目标值: {parsed_data.get('targetValue', 'N/A')}{parsed_data.get('unit', '')}")
                print(f"   时间范围: {parsed_data.get('startDate', 'N/A')} 至 {parsed_data.get('endDate', 'N/A')}")
                print(f"   验证评分: {validation.get('score', 'N/A')}/100")
                return True
            else:
                print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试目标创建功能...")
    
    # 测试语音解析
    parsing_success = test_voice_parsing()
    
    # 测试目标创建
    creation_success = test_goal_creation()
    
    print(f"\n📊 测试结果:")
    print(f"   语音解析: {'✅ 成功' if parsing_success else '❌ 失败'}")
    print(f"   目标创建: {'✅ 成功' if creation_success else '❌ 失败'}")
    
    if parsing_success and creation_success:
        print("\n🎉 所有测试通过！目标创建功能工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关组件。")

if __name__ == "__main__":
    main()
