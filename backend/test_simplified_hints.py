#!/usr/bin/env python3
"""
测试简化的语音解析提示功能
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_simplified_parsing_hints():
    """测试简化的解析提示功能"""
    print("🔍 测试简化的语音解析提示功能...")
    
    # 测试用例：不同质量的语音输入
    test_cases = [
        {
            'name': '完整目标',
            'text': '我要在3个月内通过控制饮食和每天跑步30分钟减重10斤',
            'expected_quality': 'excellent'
        },
        {
            'name': '缺少数量指标',
            'text': '我要在半年内学会游泳',
            'expected_quality': 'fair'
        },
        {
            'name': '缺少时间期限',
            'text': '我要减重10斤',
            'expected_quality': 'good'
        },
        {
            'name': '模糊表达',
            'text': '我要大概减一些体重',
            'expected_quality': 'poor'
        },
        {
            'name': '过于简单',
            'text': '我要减肥',
            'expected_quality': 'fair'
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
                    
                    # 显示解析提示
                    parsing_hints = data.get('parsing_hints', {})
                    if parsing_hints:
                        quality = parsing_hints.get('parsing_quality', 'N/A')
                        print(f"解析质量: {quality}")
                        
                        missing_elements = parsing_hints.get('missing_elements', [])
                        if missing_elements:
                            print(f"缺少元素:")
                            for j, element in enumerate(missing_elements, 1):
                                print(f"  {j}. {element}")
                    
                    # 模拟前端简化弹窗内容
                    print(f"\n📱 前端简化弹窗内容预览:")
                    simulate_simplified_frontend_modal(test_case['text'], parsing_hints)
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def simulate_simplified_frontend_modal(voiceText, parsingHints):
    """模拟前端简化弹窗内容"""
    missingElements = parsingHints.get('missing_elements', [])
    
    # 构建简化的提示内容
    content = ''
    
    # 第一部分：识别出来的内容
    content += f'识别内容：{voiceText}\n\n'
    
    # 第二部分：改进建议（最多2个）
    if missingElements:
        content += '建议改进：\n'
        
        # 将缺少元素转换为更友好的建议
        suggestionMap = {
            '明确的数量指标': '增加明确量化目标',
            '明确的时间期限': '增加明确完成时间期限',
            '明确的目标类别': '明确目标类别',
            '详细的目标描述': '提供更详细的目标描述',
            '具体明确的表达': '使用更具体的表达方式'
        }
        
        improvementSuggestions = [suggestionMap.get(element, element) for element in missingElements]
        
        # 只显示前2个建议
        for i, suggestion in enumerate(improvementSuggestions[:2], 1):
            content += f'{i}. {suggestion}\n'
    
    print("=" * 50)
    print("弹窗标题: 语音创建目标")
    print("弹窗内容:")
    print(content)
    print("按钮: [重新录音] [创建目标]")
    print("=" * 50)

def test_specific_simplified_cases():
    """测试特定简化案例"""
    print("\n🔍 测试特定简化案例...")
    
    specific_cases = [
        {
            'text': '我要学习英语口语',
            'description': '缺少明确指标和时间期限'
        },
        {
            'text': '我要在3个月内学会编程',
            'description': '缺少明确指标'
        },
        {
            'text': '我要大概读一些书',
            'description': '模糊表达，缺少具体信息'
        }
    ]
    
    for i, case in enumerate(specific_cases, 1):
        print(f"\n--- 案例 {i}: {case['description']} ---")
        print(f"输入: {case['text']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/goals/test-parse-voice",
                json={"voice_text": case['text']},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    parsing_hints = data.get('parsing_hints', {})
                    
                    # 模拟前端简化弹窗内容
                    simulate_simplified_frontend_modal(case['text'], parsing_hints)
                    
                else:
                    print(f"❌ 解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试简化的语音解析提示功能...")
    
    test_simplified_parsing_hints()
    test_specific_simplified_cases()
    
    print("\n🎉 简化语音解析提示功能测试完成！")
    print("\n📝 功能说明:")
    print("1. 移除了当前评分显示")
    print("2. 简化了提示内容结构")
    print("3. 只显示最核心的改进建议（最多2个）")
    print("4. 识别内容和改进建议有明显区隔")
    print("5. 提高了可读性和用户体验")

if __name__ == "__main__":
    main()
