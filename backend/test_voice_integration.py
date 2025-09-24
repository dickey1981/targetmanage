#!/usr/bin/env python3
"""
语音功能集成测试脚本
测试完整的语音识别、解析、验证和创建流程
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_voice_recognition_service():
    """测试语音识别服务"""
    print("🔍 测试语音识别服务...")
    
    try:
        from app.services.voice_recognition import voice_recognition_service
        
        # 检查服务可用性
        is_available = voice_recognition_service.is_available()
        print(f"   服务可用性: {is_available}")
        
        if not is_available:
            print("⚠️ 语音识别服务未配置，跳过测试")
            return False
            
        print("✅ 语音识别服务已配置")
        return True
        
    except Exception as e:
        print(f"❌ 语音识别服务测试失败: {e}")
        return False

def test_voice_parser():
    """测试语音解析器"""
    print("\n🔍 测试语音解析器...")
    
    try:
        from app.utils.voice_parser import voice_goal_parser
        
        test_cases = [
            "我要在3个月内减重10斤",
            "半年内学会游泳",
            "这个季度要完成5个项目",
            "下个月开始学习Python编程"
        ]
        
        for i, voice_text in enumerate(test_cases, 1):
            print(f"\n--- 测试用例 {i}: {voice_text} ---")
            
            try:
                parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_text)
                print("✅ 解析成功")
                print(f"   标题: {parsed_goal['title']}")
                print(f"   类别: {parsed_goal['category']}")
                print(f"   开始时间: {parsed_goal['startDate']}")
                print(f"   结束时间: {parsed_goal['endDate']}")
                print(f"   目标值: {parsed_goal['targetValue']}")
                print(f"   单位: {parsed_goal['unit']}")
                print(f"   描述: {parsed_goal['description']}")
                
            except Exception as e:
                print(f"❌ 解析失败: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ 语音解析器测试失败: {e}")
        return False

def test_goal_validator():
    """测试目标验证器"""
    print("\n🔍 测试目标验证器...")
    
    try:
        from app.utils.goal_validator import goal_validator
        
        # 创建一个测试目标数据
        test_goal = {
            'title': '我要在3个月内减重10斤',
            'category': '健康',
            'description': '通过运动和控制饮食实现减重目标',
            'startDate': '2025-01-28',
            'endDate': '2025-04-28',
            'targetValue': '10',
            'currentValue': '0',
            'unit': '斤',
            'priority': 'medium',
            'dailyReminder': True,
            'deadlineReminder': True
        }
        
        validation_result = goal_validator.validate_goal(test_goal)
        
        print("✅ 验证完成")
        print(f"   验证评分: {validation_result['score']}/100")
        print(f"   是否有效: {validation_result['is_valid']}")
        print(f"   是否有警告: {validation_result['has_warnings']}")
        
        if validation_result['errors']:
            print(f"   ❌ 错误: {validation_result['errors']}")
        if validation_result['warnings']:
            print(f"   ⚠️ 警告: {validation_result['warnings']}")
        if validation_result['suggestions']:
            print(f"   💡 建议: {validation_result['suggestions']}")
            
        return True
        
    except Exception as e:
        print(f"❌ 目标验证器测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🔍 测试API端点...")
    
    base_url = "http://localhost:8000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ 健康检查: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 测试语音解析API（不需要认证）
    try:
        test_voice_text = "我要在3个月内减重10斤"
        response = requests.post(
            f"{base_url}/api/goals/parse-voice",
            json={"voice_text": test_voice_text}
        )
        print(f"✅ 语音解析API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   解析成功: {data.get('success', False)}")
            if data.get('success'):
                parsed_data = data.get('data', {})
                print(f"   标题: {parsed_data.get('title', 'N/A')}")
                print(f"   类别: {parsed_data.get('category', 'N/A')}")
        else:
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 语音解析API测试失败: {e}")
    
    return True

def test_complete_voice_flow():
    """测试完整的语音流程"""
    print("\n🔍 测试完整语音流程...")
    
    try:
        from app.services.voice_recognition import voice_recognition_service
        from app.utils.voice_parser import voice_goal_parser
        from app.utils.goal_validator import goal_validator
        
        # 模拟语音输入
        voice_text = "我要在3个月内减重10斤"
        print(f"模拟语音输入: {voice_text}")
        
        # 1. 语音解析
        print("\n1️⃣ 语音解析...")
        parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_text)
        print(f"   解析结果: {parsed_goal['title']}")
        
        # 2. 目标验证
        print("\n2️⃣ 目标验证...")
        validation_result = goal_validator.validate_goal(parsed_goal)
        print(f"   验证评分: {validation_result['score']}/100")
        print(f"   是否有效: {validation_result['is_valid']}")
        
        # 3. 显示最终结果
        print("\n3️⃣ 最终结果...")
        if validation_result['is_valid']:
            print("✅ 目标创建流程验证通过")
            print(f"   目标标题: {parsed_goal['title']}")
            print(f"   目标类别: {parsed_goal['category']}")
            print(f"   目标值: {parsed_goal['targetValue']}{parsed_goal['unit']}")
            print(f"   时间范围: {parsed_goal['startDate']} 至 {parsed_goal['endDate']}")
        else:
            print("❌ 目标验证失败")
            print(f"   错误: {validation_result['errors']}")
            print(f"   建议: {validation_result['suggestions']}")
        
        return validation_result['is_valid']
        
    except Exception as e:
        print(f"❌ 完整语音流程测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始语音功能集成测试...")
    print("=" * 50)
    
    # 测试各个组件
    tests = [
        ("语音识别服务", test_voice_recognition_service),
        ("语音解析器", test_voice_parser),
        ("目标验证器", test_goal_validator),
        ("API端点", test_api_endpoints),
        ("完整语音流程", test_complete_voice_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！语音功能集成成功！")
    else:
        print("⚠️ 部分测试失败，请检查相关配置和代码")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
