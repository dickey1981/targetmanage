#!/usr/bin/env python3
"""
测试扩展后的时间期限检测
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_extended_deadline_detection():
    """测试扩展后的时间期限检测"""
    print("🔍 测试扩展后的时间期限检测...")
    
    # 测试用例：各种时间期限表达
    test_cases = [
        {
            'name': '具体日期前',
            'text': '11月30日前完成项目',
            'expected_has_deadline': True
        },
        {
            'name': '节日前',
            'text': '国庆前学会游泳',
            'expected_has_deadline': True
        },
        {
            'name': '春节前',
            'text': '春节前减重10斤',
            'expected_has_deadline': True
        },
        {
            'name': '年底前',
            'text': '年底前读完20本书',
            'expected_has_deadline': True
        },
        {
            'name': '学期前',
            'text': '学期前通过考试',
            'expected_has_deadline': True
        },
        {
            'name': '截止到某日',
            'text': '截止到12月25日完成',
            'expected_has_deadline': True
        },
        {
            'name': '到某日为止',
            'text': '到明年3月为止学会编程',
            'expected_has_deadline': True
        },
        {
            'name': '缺少时间期限',
            'text': '每周读一本书',
            'expected_has_deadline': False
        },
        {
            'name': '缺少时间期限',
            'text': '每天跑步',
            'expected_has_deadline': False
        },
        {
            'name': '传统时间表达',
            'text': '3个月内减重10斤',
            'expected_has_deadline': True
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
                    missing_elements = parsing_hints.get('missing_elements', [])
                    
                    # 检查是否包含"明确的时间期限"
                    has_deadline_issue = '明确的时间期限' in missing_elements
                    actual_has_deadline = not has_deadline_issue
                    
                    print(f"预期有时间期限: {test_case['expected_has_deadline']}")
                    print(f"实际检测结果: {actual_has_deadline}")
                    print(f"缺少元素: {missing_elements}")
                    
                    if actual_has_deadline == test_case['expected_has_deadline']:
                        print("✅ 检测结果正确")
                    else:
                        print("❌ 检测结果不正确")
                    
                    # 模拟前端弹窗内容
                    simulate_extended_modal(test_case['text'], parsing_hints)
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def simulate_extended_modal(voiceText, parsingHints):
    """模拟扩展后的弹窗内容"""
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
    print("扩展后的弹窗内容:")
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
    print("🚀 开始测试扩展后的时间期限检测...")
    
    test_extended_deadline_detection()
    
    print("\n🎉 扩展后的时间期限检测测试完成！")
    print("\n📝 扩展说明:")
    print("1. 添加了具体日期前表达：'11月30日前'、'号前'、'日之前'")
    print("2. 添加了节日前表达：'国庆前'、'春节前'、'中秋前'等")
    print("3. 添加了截止表达：'截止'、'到'、'为止'")
    print("4. 添加了学期表达：'学期前'、'假期前'")
    print("5. 更全面地识别各种时间期限表达")

if __name__ == "__main__":
    main()
