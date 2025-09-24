#!/usr/bin/env python3
"""
测试语音解析API的提示功能
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_voice_parsing_with_hints():
    """测试带提示的语音解析API"""
    print("🔍 测试语音解析API的提示功能...")
    
    # 测试用例：不同质量的语音输入
    test_cases = [
        {
            'name': '完整目标',
            'text': '我要在3个月内通过控制饮食和每天跑步30分钟减重10斤'
        },
        {
            'name': '缺少数量指标',
            'text': '我要在半年内学会游泳'
        },
        {
            'name': '缺少时间期限',
            'text': '我要减重10斤'
        },
        {
            'name': '模糊表达',
            'text': '我要大概减一些体重'
        },
        {
            'name': '过于简单',
            'text': '我要减肥'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['name']} ---")
        print(f"语音输入: {test_case['text']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/goals/test-parse-voice",
                json={"voice_text": test_case['text']},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ 语音解析成功")
                    
                    # 显示解析结果
                    parsed_data = data.get('data', {})
                    print(f"解析结果:")
                    print(f"  标题: {parsed_data.get('title', 'N/A')}")
                    print(f"  类别: {parsed_data.get('category', 'N/A')}")
                    print(f"  目标值: {parsed_data.get('targetValue', 'N/A')}{parsed_data.get('unit', '')}")
                    print(f"  开始时间: {parsed_data.get('startDate', 'N/A')}")
                    print(f"  结束时间: {parsed_data.get('endDate', 'N/A')}")
                    
                    # 显示解析提示
                    parsing_hints = data.get('parsing_hints', {})
                    if parsing_hints:
                        print(f"解析质量: {parsing_hints.get('parsing_quality', 'N/A')}")
                        
                        missing_elements = parsing_hints.get('missing_elements', [])
                        if missing_elements:
                            print(f"缺少元素: {', '.join(missing_elements)}")
                        
                        suggestions = parsing_hints.get('suggestions', [])
                        if suggestions:
                            print(f"建议: {suggestions[0]}")
                        
                        improvement_tips = parsing_hints.get('improvement_tips', [])
                        if improvement_tips:
                            print(f"改进提示:")
                            for tip in improvement_tips[:2]:  # 只显示前2个提示
                                print(f"  {tip}")
                    
                    # 显示验证结果
                    validation = data.get('validation', {})
                    if validation:
                        print(f"验证评分: {validation.get('score', 'N/A')}/100")
                        print(f"是否有效: {'✅' if validation.get('is_valid') else '❌'}")
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_specific_parsing_issues():
    """测试特定解析问题的提示"""
    print("\n🔍 测试特定解析问题的提示...")
    
    specific_issues = [
        {
            'issue': '缺少明确指标',
            'text': '我要在3个月内学会编程',
            'expected_hint': '明确的数量指标'
        },
        {
            'issue': '缺少时间期限',
            'text': '我要减重10斤',
            'expected_hint': '明确的时间期限'
        },
        {
            'issue': '模糊表达',
            'text': '我要大概读一些书',
            'expected_hint': '具体明确的表达'
        },
        {
            'issue': '过于简单',
            'text': '我要学习',
            'expected_hint': '详细的目标描述'
        }
    ]
    
    for i, issue in enumerate(specific_issues, 1):
        print(f"\n--- 问题 {i}: {issue['issue']} ---")
        print(f"输入: {issue['text']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/goals/test-parse-voice",
                json={"voice_text": issue['text']},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    parsing_hints = data.get('parsing_hints', {})
                    missing_elements = parsing_hints.get('missing_elements', [])
                    
                    print(f"检测到的缺少元素: {missing_elements}")
                    print(f"预期提示: {issue['expected_hint']}")
                    
                    if issue['expected_hint'] in missing_elements:
                        print("✅ 正确检测到问题")
                    else:
                        print("❌ 未检测到预期问题")
                    
                    # 显示改进建议
                    improvement_tips = parsing_hints.get('improvement_tips', [])
                    if improvement_tips:
                        print(f"改进建议: {improvement_tips[0]}")
                        
                else:
                    print(f"❌ 解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试语音解析API的提示功能...")
    
    test_voice_parsing_with_hints()
    test_specific_parsing_issues()
    
    print("\n🎉 语音解析API提示功能测试完成！")
    print("\n📝 功能说明:")
    print("1. 系统会分析语音输入的质量和完整性")
    print("2. 提供具体的缺少元素提示")
    print("3. 给出详细的改进建议和示例")
    print("4. 帮助用户完善目标描述")

if __name__ == "__main__":
    main()
