#!/usr/bin/env python3
"""
测试语音解析提示功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.voice_parser import voice_goal_parser
from app.utils.goal_validator import goal_validator

def test_voice_parsing_hints():
    """测试语音解析提示功能"""
    print("🔍 测试语音解析提示功能...")
    
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
        },
        {
            'name': '缺少类别信息',
            'text': '我要读10本书'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['name']} ---")
        print(f"语音输入: {test_case['text']}")
        
        try:
            # 解析语音文本
            parsed_goal = voice_goal_parser.parse_voice_to_goal(test_case['text'])
            
            # 显示解析结果
            print(f"解析结果:")
            print(f"  标题: {parsed_goal.get('title', 'N/A')}")
            print(f"  类别: {parsed_goal.get('category', 'N/A')}")
            print(f"  目标值: {parsed_goal.get('targetValue', 'N/A')}{parsed_goal.get('unit', '')}")
            print(f"  开始时间: {parsed_goal.get('startDate', 'N/A')}")
            print(f"  结束时间: {parsed_goal.get('endDate', 'N/A')}")
            
            # 显示解析提示
            parsing_hints = parsed_goal.get('parsing_hints', {})
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
            
            # 验证目标
            validation = goal_validator.validate_goal(parsed_goal)
            print(f"验证评分: {validation.get('score', 'N/A')}/100")
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")

def test_parsing_quality_assessment():
    """测试解析质量评估"""
    print("\n🔍 测试解析质量评估...")
    
    quality_examples = [
        {
            'text': '我要在3个月内通过控制饮食和每天跑步30分钟减重10斤',
            'expected_quality': 'excellent'
        },
        {
            'text': '我要在半年内学会游泳',
            'expected_quality': 'good'
        },
        {
            'text': '我要减重10斤',
            'expected_quality': 'fair'
        },
        {
            'text': '我要大概减一些体重',
            'expected_quality': 'poor'
        }
    ]
    
    for i, example in enumerate(quality_examples, 1):
        print(f"\n--- 质量评估 {i} ---")
        print(f"输入: {example['text']}")
        
        parsed_goal = voice_goal_parser.parse_voice_to_goal(example['text'])
        parsing_hints = parsed_goal.get('parsing_hints', {})
        actual_quality = parsing_hints.get('parsing_quality', 'unknown')
        
        print(f"预期质量: {example['expected_quality']}")
        print(f"实际质量: {actual_quality}")
        print(f"评估结果: {'✅ 正确' if actual_quality == example['expected_quality'] else '❌ 错误'}")

def test_improvement_suggestions():
    """测试改进建议生成"""
    print("\n🔍 测试改进建议生成...")
    
    improvement_cases = [
        {
            'text': '我要减肥',
            'expected_missing': ['明确的数量指标', '明确的时间期限', '详细的目标描述']
        },
        {
            'text': '我要在3个月内减重10斤',
            'expected_missing': []
        },
        {
            'text': '我要大概减一些体重',
            'expected_missing': ['明确的数量指标', '明确的时间期限', '具体明确的表达']
        }
    ]
    
    for i, case in enumerate(improvement_cases, 1):
        print(f"\n--- 改进建议 {i} ---")
        print(f"输入: {case['text']}")
        
        parsed_goal = voice_goal_parser.parse_voice_to_goal(case['text'])
        parsing_hints = parsed_goal.get('parsing_hints', {})
        missing_elements = parsing_hints.get('missing_elements', [])
        
        print(f"检测到的缺少元素: {missing_elements}")
        print(f"预期的缺少元素: {case['expected_missing']}")
        
        # 检查是否检测到了预期的缺少元素
        missing_found = all(element in missing_elements for element in case['expected_missing'])
        extra_found = len(missing_elements) == len(case['expected_missing'])
        
        print(f"检测结果: {'✅ 准确' if missing_found and extra_found else '⚠️ 部分准确'}")

def main():
    """主测试函数"""
    print("🚀 开始测试语音解析提示功能...")
    
    test_voice_parsing_hints()
    test_parsing_quality_assessment()
    test_improvement_suggestions()
    
    print("\n🎉 语音解析提示功能测试完成！")

if __name__ == "__main__":
    main()
