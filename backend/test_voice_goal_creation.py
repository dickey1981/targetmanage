#!/usr/bin/env python3
"""
语音目标创建测试
"""
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_voice_goal_creation():
    """测试语音目标创建流程"""
    print("🚀 测试语音目标创建流程...")
    
    try:
        from app.utils.voice_parser import voice_goal_parser
        from app.utils.goal_validator import goal_validator
        
        # 测试语音输入
        voice_text = "我要在3个月内减重10斤"
        print(f"语音输入: {voice_text}")
        
        # 1. 语音解析
        print("\n1️⃣ 语音解析...")
        parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_text)
        print(f"解析结果:")
        print(f"  标题: {parsed_goal['title']}")
        print(f"  类别: {parsed_goal['category']}")
        print(f"  目标值: {parsed_goal['targetValue']}{parsed_goal['unit']}")
        print(f"  时间范围: {parsed_goal['startDate']} 至 {parsed_goal['endDate']}")
        
        # 2. 目标验证
        print("\n2️⃣ 目标验证...")
        validation_result = goal_validator.validate_goal(parsed_goal)
        print(f"验证结果:")
        print(f"  评分: {validation_result['score']}/100")
        print(f"  是否有效: {validation_result['is_valid']}")
        
        if validation_result['warnings']:
            print(f"  警告: {validation_result['warnings']}")
        if validation_result['suggestions']:
            print(f"  建议: {validation_result['suggestions']}")
        
        # 3. 最终结果
        print("\n3️⃣ 最终结果...")
        if validation_result['is_valid']:
            print("✅ 目标创建流程验证通过！")
            print("可以创建目标:")
            print(f"  📝 {parsed_goal['title']}")
            print(f"  🏷️ 类别: {parsed_goal['category']}")
            print(f"  🎯 目标: {parsed_goal['targetValue']}{parsed_goal['unit']}")
            print(f"  📅 时间: {parsed_goal['startDate'][:10]} 至 {parsed_goal['endDate'][:10]}")
        else:
            print("❌ 目标验证失败")
            print(f"错误: {validation_result['errors']}")
        
        return validation_result['is_valid']
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_voice_goal_creation()
    print(f"\n测试结果: {'✅ 成功' if success else '❌ 失败'}")
    sys.exit(0 if success else 1)
