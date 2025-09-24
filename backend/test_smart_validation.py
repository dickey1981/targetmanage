#!/usr/bin/env python3
"""
测试SMART原则验证功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.goal_validator import goal_validator
from datetime import datetime, timedelta

def test_smart_validation():
    """测试SMART原则验证功能"""
    print("🔍 测试SMART原则验证功能...")
    
    # 测试用例：不同质量的目标
    test_cases = [
        {
            'name': '优秀目标',
            'data': {
                'title': '我要在3个月内减重10斤',
                'category': '健康',
                'description': '通过控制饮食和每天跑步30分钟，在3个月内减重10斤',
                'startDate': datetime.now().isoformat(),
                'endDate': (datetime.now() + timedelta(days=90)).isoformat(),
                'targetValue': '10',
                'currentValue': '0',
                'unit': '斤',
                'priority': 'medium',
                'dailyReminder': True,
                'deadlineReminder': True
            }
        },
        {
            'name': '模糊目标',
            'data': {
                'title': '我要减肥',
                'category': '健康',
                'description': '大概减一些体重',
                'startDate': datetime.now().isoformat(),
                'endDate': (datetime.now() + timedelta(days=30)).isoformat(),
                'targetValue': '',
                'currentValue': '0',
                'unit': '',
                'priority': 'medium',
                'dailyReminder': True,
                'deadlineReminder': True
            }
        },
        {
            'name': '过于困难的目标',
            'data': {
                'title': '我要在1个月内减重50斤',
                'category': '健康',
                'description': '通过极端节食在1个月内减重50斤',
                'startDate': datetime.now().isoformat(),
                'endDate': (datetime.now() + timedelta(days=30)).isoformat(),
                'targetValue': '50',
                'currentValue': '0',
                'unit': '斤',
                'priority': 'high',
                'dailyReminder': True,
                'deadlineReminder': True
            }
        },
        {
            'name': '时间过短的目标',
            'data': {
                'title': '我要在3天内学会编程',
                'category': '学习',
                'description': '在3天内掌握Python编程',
                'startDate': datetime.now().isoformat(),
                'endDate': (datetime.now() + timedelta(days=3)).isoformat(),
                'targetValue': '1',
                'currentValue': '0',
                'unit': '门技能',
                'priority': 'high',
                'dailyReminder': True,
                'deadlineReminder': True
            }
        },
        {
            'name': '缺少类别的目标',
            'data': {
                'title': '我要读10本书',
                'category': '',
                'description': '在半年内读完10本技术书籍',
                'startDate': datetime.now().isoformat(),
                'endDate': (datetime.now() + timedelta(days=180)).isoformat(),
                'targetValue': '10',
                'currentValue': '0',
                'unit': '本书',
                'priority': 'medium',
                'dailyReminder': True,
                'deadlineReminder': True
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['name']} ---")
        
        try:
            # 验证目标
            validation_result = goal_validator.validate_goal(test_case['data'])
            
            # 显示基本验证结果
            print(f"   总体评分: {validation_result['score']}/100")
            print(f"   是否有效: {'✅' if validation_result['is_valid'] else '❌'}")
            print(f"   有警告: {'⚠️' if validation_result['has_warnings'] else '✅'}")
            
            # 显示SMART原则得分
            smart_scores = validation_result.get('smart_scores', {})
            print(f"   SMART原则得分:")
            for principle, score in smart_scores.items():
                principle_name = goal_validator._get_principle_name(principle)
                score_percent = int(score * 100)
                print(f"     {principle_name}: {score_percent}%")
            
            # 显示SMART分析
            smart_analysis = validation_result.get('smart_analysis', {})
            if smart_analysis:
                print(f"   总体SMART得分: {int(smart_analysis['overall_score'] * 100)}%")
                if smart_analysis['strengths']:
                    print(f"   优势: {', '.join(smart_analysis['strengths'])}")
                if smart_analysis['weaknesses']:
                    print(f"   需要改进: {', '.join(smart_analysis['weaknesses'])}")
            
            # 显示错误和警告
            if validation_result['errors']:
                print(f"   错误: {validation_result['errors'][0]}")
            if validation_result['warnings']:
                print(f"   警告: {validation_result['warnings'][0]}")
            if validation_result['suggestions']:
                print(f"   建议: {validation_result['suggestions'][0]}")
            
        except Exception as e:
            print(f"❌ 验证失败: {e}")

def test_specificity_analysis():
    """测试具体性分析功能"""
    print("\n🔍 测试具体性分析功能...")
    
    test_texts = [
        "我要在3个月内减重10斤",
        "我要大概减一些体重",
        "我要在2024年12月31日前完成5个项目",
        "我要可能学会一些技能",
        "我要每天跑步30分钟，持续3个月"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 文本 {i}: {text} ---")
        specificity_score = goal_validator._analyze_specificity(text)
        print(f"   具体性得分: {int(specificity_score * 100)}%")
        
        if specificity_score >= 0.8:
            print("   评价: 非常具体")
        elif specificity_score >= 0.6:
            print("   评价: 比较具体")
        elif specificity_score >= 0.4:
            print("   评价: 一般具体")
        else:
            print("   评价: 较为模糊")

def test_achievability_assessment():
    """测试可实现性评估功能"""
    print("\n🔍 测试可实现性评估功能...")
    
    test_scenarios = [
        {'category': '健康', 'target': 10, 'duration': 90, 'daily': 0.11},
        {'category': '健康', 'target': 50, 'duration': 30, 'daily': 1.67},
        {'category': '学习', 'target': 5, 'duration': 180, 'daily': 0.03},
        {'category': '工作', 'target': 20, 'duration': 60, 'daily': 0.33},
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- 场景 {i}: {scenario} ---")
        achievability_score = goal_validator._assess_achievability(
            scenario['category'], scenario['target'], scenario['duration'], scenario['daily']
        )
        print(f"   可实现性得分: {int(achievability_score * 100)}%")
        
        if achievability_score >= 0.8:
            print("   评价: 很容易实现")
        elif achievability_score >= 0.6:
            print("   评价: 可以实现")
        elif achievability_score >= 0.4:
            print("   评价: 有挑战性")
        else:
            print("   评价: 过于困难")

def main():
    """主测试函数"""
    print("🚀 开始测试SMART原则验证功能...")
    
    test_smart_validation()
    test_specificity_analysis()
    test_achievability_assessment()
    
    print("\n🎉 SMART原则验证测试完成！")

if __name__ == "__main__":
    main()
