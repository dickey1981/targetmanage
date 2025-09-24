#!/usr/bin/env python3
"""
测试SMART原则验证API
"""

import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

def test_smart_validation_api():
    """测试SMART原则验证API"""
    print("🔍 测试SMART原则验证API...")
    
    # 测试用例：优秀目标
    excellent_goal = {
        "title": "我要在3个月内减重10斤",
        "category": "健康",
        "description": "通过控制饮食和每天跑步30分钟，在3个月内减重10斤",
        "startDate": datetime.now().strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "targetValue": "10",
        "currentValue": "0",
        "unit": "斤",
        "priority": "medium",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/goals/test-validate-smart",
            json=excellent_goal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                validation_data = data.get('data', {})
                print("✅ SMART原则验证成功")
                print(f"   总体评分: {validation_data.get('score', 'N/A')}/100")
                print(f"   是否有效: {'✅' if validation_data.get('is_valid') else '❌'}")
                
                # 显示SMART原则得分
                smart_scores = validation_data.get('smart_scores', {})
                if smart_scores:
                    print("   SMART原则得分:")
                    for principle, score in smart_scores.items():
                        principle_names = {
                            'specific': '具体性',
                            'measurable': '可衡量性',
                            'achievable': '可实现性',
                            'relevant': '相关性',
                            'time_bound': '时限性'
                        }
                        principle_name = principle_names.get(principle, principle)
                        score_percent = int(score * 100)
                        print(f"     {principle_name}: {score_percent}%")
                
                # 显示SMART分析
                smart_analysis = validation_data.get('smart_analysis', {})
                if smart_analysis:
                    print(f"   总体SMART得分: {int(smart_analysis['overall_score'] * 100)}%")
                    if smart_analysis.get('strengths'):
                        print(f"   优势: {', '.join(smart_analysis['strengths'])}")
                    if smart_analysis.get('weaknesses'):
                        print(f"   需要改进: {', '.join(smart_analysis['weaknesses'])}")
                
                # 显示建议
                suggestions = validation_data.get('suggestions', [])
                if suggestions:
                    print(f"   建议: {suggestions[0]}")
                
                return True
            else:
                print(f"❌ SMART原则验证失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_poor_goal_validation():
    """测试较差目标的验证"""
    print("\n🔍 测试较差目标的SMART原则验证...")
    
    # 测试用例：模糊目标
    poor_goal = {
        "title": "我要减肥",
        "category": "健康",
        "description": "大概减一些体重",
        "startDate": datetime.now().strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "targetValue": "",
        "currentValue": "0",
        "unit": "",
        "priority": "medium",
        "dailyReminder": True,
        "deadlineReminder": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/goals/test-validate-smart",
            json=poor_goal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                validation_data = data.get('data', {})
                print("✅ 模糊目标验证完成")
                print(f"   总体评分: {validation_data.get('score', 'N/A')}/100")
                print(f"   是否有效: {'✅' if validation_data.get('is_valid') else '❌'}")
                
                # 显示错误和警告
                errors = validation_data.get('errors', [])
                warnings = validation_data.get('warnings', [])
                if errors:
                    print(f"   错误: {errors[0]}")
                if warnings:
                    print(f"   警告: {warnings[0]}")
                
                # 显示SMART原则得分
                smart_scores = validation_data.get('smart_scores', {})
                if smart_scores:
                    print("   SMART原则得分:")
                    for principle, score in smart_scores.items():
                        principle_names = {
                            'specific': '具体性',
                            'measurable': '可衡量性',
                            'achievable': '可实现性',
                            'relevant': '相关性',
                            'time_bound': '时限性'
                        }
                        principle_name = principle_names.get(principle, principle)
                        score_percent = int(score * 100)
                        print(f"     {principle_name}: {score_percent}%")
                
                return True
            else:
                print(f"❌ 验证失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试SMART原则验证API...")
    
    excellent_success = test_smart_validation_api()
    poor_success = test_poor_goal_validation()
    
    print("\n📊 测试结果:")
    print(f"   优秀目标验证: {'✅ 成功' if excellent_success else '❌ 失败'}")
    print(f"   模糊目标验证: {'✅ 成功' if poor_success else '❌ 失败'}")
    
    if excellent_success and poor_success:
        print("\n🎉 所有SMART原则验证API测试通过！")
        print("\n📝 功能说明:")
        print("1. 系统会根据SMART原则对目标进行全面评估")
        print("2. 提供具体的改进建议和评分")
        print("3. 帮助用户制定更有效的目标")
    else:
        print("\n⚠️ 部分测试失败，请检查相关组件。")

if __name__ == "__main__":
    main()
