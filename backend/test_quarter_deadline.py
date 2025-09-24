#!/usr/bin/env python3
"""
测试季度相关的时间期限检测
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_quarter_deadline_detection():
    """测试季度相关的时间期限检测"""
    print("🔍 测试季度相关的时间期限检测...")
    
    # 测试用例：季度相关的时间期限表达
    test_cases = [
        {
            'name': '这个季度',
            'text': '这个季度要完成5个项目',
            'expected_has_deadline': True
        },
        {
            'name': '下个季度',
            'text': '下个季度学会编程',
            'expected_has_deadline': True
        },
        {
            'name': '第一季度',
            'text': '第一季度减重10斤',
            'expected_has_deadline': True
        },
        {
            'name': '第二季度',
            'text': '第二季度读完20本书',
            'expected_has_deadline': True
        },
        {
            'name': '第三季度',
            'text': '第三季度通过考试',
            'expected_has_deadline': True
        },
        {
            'name': '第四季度',
            'text': '第四季度完成项目',
            'expected_has_deadline': True
        },
        {
            'name': 'Q1',
            'text': 'Q1学会游泳',
            'expected_has_deadline': True
        },
        {
            'name': 'Q2',
            'text': 'Q2减重目标',
            'expected_has_deadline': True
        },
        {
            'name': '季度内',
            'text': '季度内完成所有任务',
            'expected_has_deadline': True
        },
        {
            'name': '季度前',
            'text': '季度前学会新技能',
            'expected_has_deadline': True
        },
        {
            'name': '缺少时间期限',
            'text': '每周读一本书',
            'expected_has_deadline': False
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
                    simulate_quarter_modal(test_case['text'], parsing_hints)
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def simulate_quarter_modal(voiceText, parsingHints):
    """模拟季度相关的弹窗内容"""
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
    print("季度相关的弹窗内容:")
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
    print("🚀 开始测试季度相关的时间期限检测...")
    
    test_quarter_deadline_detection()
    
    print("\n🎉 季度相关的时间期限检测测试完成！")
    print("\n📝 季度扩展说明:")
    print("1. 添加了季度表达：'季度'、'这个季度'、'下个季度'")
    print("2. 添加了具体季度：'第一季度'、'第二季度'、'第三季度'、'第四季度'")
    print("3. 添加了季度英文：'Q1'、'Q2'、'Q3'、'Q4'")
    print("4. 添加了季度相关：'季度内'、'季度前'")
    print("5. 现在'这个季度要完成5个项目'不会显示'缺少明确时间期限'")

if __name__ == "__main__":
    main()
