#!/usr/bin/env python3
"""
测试统一的语音解析提示功能
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_unified_parsing_hints():
    """测试统一的解析提示功能"""
    print("🔍 测试统一的语音解析提示功能...")
    
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
                        
                        improvement_tips = parsing_hints.get('improvement_tips', [])
                        if improvement_tips:
                            print(f"改进建议:")
                            for j, tip in enumerate(improvement_tips, 1):
                                clean_tip = tip.replace('示例：', '').replace('💡 ', '')
                                print(f"  {j}. {clean_tip}")
                    
                    # 显示验证结果
                    validation = data.get('validation', {})
                    if validation:
                        print(f"验证评分: {validation.get('score', 'N/A')}/100")
                    
                    # 模拟前端弹窗内容
                    print(f"\n📱 前端弹窗内容预览:")
                    self.simulate_frontend_modal(test_case['text'], parsing_hints, validation)
                    
                else:
                    print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def simulate_frontend_modal(voiceText, parsingHints, validation):
    """模拟前端弹窗内容"""
    quality = parsingHints.get('parsing_quality', 'unknown')
    missingElements = parsingHints.get('missing_elements', [])
    improvementTips = parsingHints.get('improvement_tips', [])
    
    # 构建提示内容
    content = f'识别到："{voiceText}"\n\n'
    
    # 添加解析质量说明
    qualityText = {
        'excellent': '目标描述非常完整',
        'good': '目标描述基本完整',
        'fair': '目标描述需要完善',
        'poor': '目标描述过于简单'
    }
    
    if qualityText.get(quality):
        content += qualityText[quality]
    
    # 添加缺少元素列表（1、2、3竖排显示）
    if missingElements:
        content += '，建议优化：\n\n检测到以下问题：\n'
        for i, element in enumerate(missingElements, 1):
            content += f'{i}. {element}\n'
        content += '\n'
    
    # 添加改进建议（1、2、3竖排显示）
    if improvementTips:
        content += '改进建议：\n'
        for i, tip in enumerate(improvementTips, 1):
            cleanTip = tip.replace('示例：', '').replace('💡 ', '')
            content += f'{i}. {cleanTip}\n'
    
    # 添加验证评分信息
    if validation and validation.get('score'):
        content += f'\n当前评分：{validation["score"]}/100'
    
    print("=" * 50)
    print("弹窗标题: 语音创建目标")
    print("弹窗内容:")
    print(content)
    print("按钮: [重新录音] [创建目标]")
    print("=" * 50)

def test_specific_hint_cases():
    """测试特定提示案例"""
    print("\n🔍 测试特定提示案例...")
    
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
                    validation = data.get('validation', {})
                    
                    # 模拟前端弹窗内容
                    simulate_frontend_modal(case['text'], parsing_hints, validation)
                    
                else:
                    print(f"❌ 解析失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试统一的语音解析提示功能...")
    
    test_unified_parsing_hints()
    test_specific_hint_cases()
    
    print("\n🎉 统一语音解析提示功能测试完成！")
    print("\n📝 功能说明:")
    print("1. 所有提示信息整合到一个弹窗中")
    print("2. 问题列表以1、2、3竖排方式清晰展示")
    print("3. 改进建议以1、2、3竖排方式清晰展示")
    print("4. 包含解析质量说明和验证评分")
    print("5. 提供重新录音和创建目标两个选项")

if __name__ == "__main__":
    main()
