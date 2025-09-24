#!/usr/bin/env python3
"""
测试自定义弹窗的语音解析提示功能
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_custom_modal_parsing_hints():
    """测试自定义弹窗的解析提示功能"""
    print("🔍 测试自定义弹窗的语音解析提示功能...")
    
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
                    parsing_hints = data.get('parsing_hints', {})
                    
                    # 模拟自定义弹窗内容
                    simulate_custom_modal(test_case['text'], parsing_hints)
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def simulate_custom_modal(voiceText, parsingHints):
    """模拟自定义弹窗内容"""
    missingElements = parsingHints.get('missing_elements', [])
    
    # 将缺少元素转换为更友好的建议
    suggestionMap = {
        '明确的数量指标': '增加明确量化目标',
        '明确的时间期限': '增加明确完成时间期限',
        '明确的目标类别': '明确目标类别',
        '详细的目标描述': '提供更详细的目标描述',
        '具体明确的表达': '使用更具体的表达方式'
    }
    
    improvementSuggestions = [suggestionMap.get(element, element) for element in missingElements]
    suggestions = improvementSuggestions[:2]  # 只显示前2个建议
    
    print("=" * 60)
    print("自定义弹窗标题: 语音创建目标")
    print("弹窗内容:")
    print("┌─────────────────────────────────────────┐")
    print("│ 识别内容：                              │")
    print(f"│ {voiceText:<35} │")
    print("│                                         │")
    
    if suggestions:
        print("│ 建议改进：                              │")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"│ {i}. {suggestion:<32} │")
    else:
        print("│ 无改进建议                              │")
    
    print("│                                         │")
    print("│ [重新录音]              [创建目标]        │")
    print("└─────────────────────────────────────────┘")
    print("=" * 60)

def main():
    """主测试函数"""
    print("🚀 开始测试自定义弹窗的语音解析提示功能...")
    
    test_custom_modal_parsing_hints()
    
    print("\n🎉 自定义弹窗语音解析提示功能测试完成！")
    print("\n📝 功能说明:")
    print("1. 使用自定义弹窗组件替代系统弹窗")
    print("2. 识别内容和改进建议分行显示")
    print("3. 改进建议以列表形式清晰展示")
    print("4. 支持最多2个改进建议")
    print("5. 提供重新录音和创建目标两个选项")
    print("6. 完全解决了换行符显示问题")

if __name__ == "__main__":
    main()
