#!/usr/bin/env python3
"""
测试语音目标创建功能
"""
import requests
import json

def test_voice_goal_creation():
    """测试语音目标创建功能"""
    
    print("🚀 测试语音目标创建功能...")
    
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
            result = response.json()
            if result.get("success") and result.get("data", {}).get("token"):
                token = result["data"]["token"]
                print("✅ 登录成功")
            else:
                print(f"❌ 登录响应格式错误: {result}")
                return
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试语音文本解析
    print("\n🔍 测试语音文本解析...")
    test_cases = [
        "我要在3个月内减重10斤",
        "半年内学会游泳",
        "这个季度要完成5个项目",
        "下个月开始学习Python编程"
    ]
    
    for i, voice_text in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {voice_text} ---")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/goals/parse-voice",
                json={"voice_text": voice_text},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 解析成功")
                print(f"   标题: {result['data']['title']}")
                print(f"   类别: {result['data']['category']}")
                print(f"   开始时间: {result['data']['startDate']}")
                print(f"   结束时间: {result['data']['endDate']}")
                print(f"   目标值: {result['data']['targetValue']}")
                print(f"   单位: {result['data']['unit']}")
                
                # 显示验证结果
                validation = result['validation']
                print(f"   验证评分: {validation['score']}/100")
                if validation['errors']:
                    print(f"   ❌ 错误: {validation['errors']}")
                if validation['warnings']:
                    print(f"   ⚠️ 警告: {validation['warnings']}")
                if validation['suggestions']:
                    print(f"   💡 建议: {validation['suggestions']}")
                    
            else:
                print(f"❌ 解析失败: {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    # 3. 测试语音目标创建
    print("\n🎯 测试语音目标创建...")
    test_goal = "我要在2个月内减重15斤"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/goals/create-from-voice",
            json={"voice_text": test_goal},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 目标创建成功")
            print(f"   目标ID: {result['data']['id']}")
            print(f"   标题: {result['data']['title']}")
            print(f"   类别: {result['data']['category']}")
            print(f"   状态: {result['data']['status']}")
            print(f"   剩余天数: {result['data']['remaining_days']}天")
        else:
            print(f"❌ 目标创建失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 目标创建测试失败: {e}")
    
    # 4. 验证目标是否真的创建成功
    print("\n📋 验证目标列表...")
    try:
        response = requests.get("http://localhost:8000/api/goals/", headers=headers)
        
        if response.status_code == 200:
            goals = response.json()
            print(f"✅ 获取到 {len(goals)} 个目标")
            
            # 查找刚创建的目标
            for goal in goals:
                if "减重" in goal.get('title', ''):
                    print(f"   找到减重目标: {goal['title']}")
                    print(f"   进度: {goal.get('progress', 0)}%")
                    print(f"   状态: {goal.get('status', 'N/A')}")
                    break
        else:
            print(f"❌ 获取目标列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 验证目标列表失败: {e}")
    
    print("\n✨ 语音目标创建功能测试完成！")

if __name__ == "__main__":
    test_voice_goal_creation()
