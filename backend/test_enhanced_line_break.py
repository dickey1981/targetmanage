#!/usr/bin/env python3
"""
测试增强分行显示的语音解析提示功能
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_enhanced_line_break_parsing_hints():
    """测试增强分行显示的解析提示功能"""
    print("🔍 测试增强分行显示的语音解析提示功能...")
    
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
                    
                    # 模拟前端增强分行弹窗内容
                    simulate_enhanced_line_break_modal(test_case['text'], parsing_hints)
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def simulate_enhanced_line_break_modal(voiceText, parsingHints):
    """模拟前端增强分行弹窗内容"""
    missingElements = parsingHints.get('missing_elements', [])
    
    # 构建增强分行的提示内容
    content = ''
    
    # 第一部分：识别出来的内容（增强分行显示）
    content += f'识别内容：\n\n{voiceText}\n\n\n'
    
    # 第二部分：改进建议（最多2个）
    if missingElements:
        content += '建议改进：\n\n'
        
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
            content += f'{i}. {suggestion}\n\n'
    
    print("=" * 60)
    print("弹窗标题: 语音创建目标")
    print("弹窗内容:")
    print(content)
    print("按钮: [重新录音] [创建目标]")
    print("=" * 60)

def main():
    """主测试函数"""
    print("🚀 开始测试增强分行显示的语音解析提示功能...")
    
    test_enhanced_line_break_parsing_hints()
    
    print("\n🎉 增强分行显示语音解析提示功能测试完成！")
    print("\n📝 功能说明:")
    print("1. 使用多个换行符确保分行显示")
    print("2. '识别内容：' 和实际内容之间有明显的空行")
    print("3. '建议改进：' 和具体建议之间有明显的空行")
    print("4. 两个部分之间有多个空行分隔")
    print("5. 每个建议之间也有空行分隔")
    print("6. 提高了弹窗内容的可读性和层次感")

if __name__ == "__main__":
    main()
