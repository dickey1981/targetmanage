#!/usr/bin/env python3
"""
测试时间解析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.voice_parser import voice_goal_parser
from app.utils.goal_validator import goal_validator
from datetime import datetime

def test_time_parsing():
    """测试时间解析功能"""
    print("🔍 测试时间解析功能...")
    
    test_cases = [
        "我要在3个月内减重10斤",
        "半年内学会游泳",
        "这个季度要完成5个项目",
        "下个月开始学习Python编程",
        "每天跑步30分钟",
        "每周读一本书"
    ]
    
    for i, voice_text in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {voice_text} ---")
        
        try:
            # 解析语音文本
            parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_text)
            
            # 验证解析结果
            validation = goal_validator.validate_goal(parsed_goal)
            
            print(f"   开始时间: {parsed_goal.get('startDate', 'N/A')}")
            print(f"   结束时间: {parsed_goal.get('endDate', 'N/A')}")
            print(f"   验证评分: {validation.get('score', 'N/A')}/100")
            
            # 检查是否有时间相关的警告
            time_warnings = [w for w in validation.get('warnings', []) if '时间' in w]
            if time_warnings:
                print(f"   ⚠️ 时间警告: {time_warnings[0]}")
            else:
                print("   ✅ 时间设置正常")
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")

def test_current_time():
    """测试当前时间处理"""
    print("\n🔍 测试当前时间处理...")
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"   当前时间: {now}")
    print(f"   今天开始: {today_start}")
    print(f"   时间差: {(now - today_start).total_seconds()} 秒")
    
    # 测试语音解析器生成的时间
    parsed_goal = voice_goal_parser.parse_voice_to_goal("我要在3个月内减重10斤")
    start_date_str = parsed_goal.get('startDate')
    
    if start_date_str:
        start_date = datetime.fromisoformat(start_date_str)
        print(f"   解析的开始时间: {start_date}")
        print(f"   是否等于今天开始: {start_date == today_start}")

def main():
    """主测试函数"""
    print("🚀 开始测试时间解析功能...")
    
    test_current_time()
    test_time_parsing()
    
    print("\n🎉 时间解析测试完成！")

if __name__ == "__main__":
    main()
