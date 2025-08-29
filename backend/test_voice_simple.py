#!/usr/bin/env python3
"""
简单测试语音功能（不需要登录）
"""
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_voice_parser():
    """测试语音解析器"""
    print("🔍 测试语音解析器...")
    
    try:
        from app.utils.voice_parser import voice_goal_parser
        
        test_cases = [
            "我要在3个月内减重10斤",
            "半年内学会游泳",
            "这个季度要完成5个项目",
            "下个月开始学习Python编程"
        ]
        
        for i, voice_text in enumerate(test_cases, 1):
            print(f"\n--- 测试用例 {i}: {voice_text} ---")
            
            try:
                parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_text)
                print("✅ 解析成功")
                print(f"   标题: {parsed_goal['title']}")
                print(f"   类别: {parsed_goal['category']}")
                print(f"   开始时间: {parsed_goal['startDate']}")
                print(f"   结束时间: {parsed_goal['endDate']}")
                print(f"   目标值: {parsed_goal['targetValue']}")
                print(f"   单位: {parsed_goal['unit']}")
                print(f"   描述: {parsed_goal['description']}")
                
            except Exception as e:
                print(f"❌ 解析失败: {e}")
                
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_goal_validator():
    """测试目标验证器"""
    print("\n🔍 测试目标验证器...")
    
    try:
        from app.utils.goal_validator import goal_validator
        
        # 创建一个测试目标数据
        test_goal = {
            'title': '我要在3个月内减重10斤',
            'category': '健康',
            'description': '通过运动和控制饮食实现减重目标',
            'startDate': '2025-01-28',
            'endDate': '2025-04-28',
            'targetValue': '10',
            'currentValue': '0',
            'unit': '斤',
            'priority': 'medium',
            'dailyReminder': True,
            'deadlineReminder': True
        }
        
        validation_result = goal_validator.validate_goal(test_goal)
        
        print("✅ 验证完成")
        print(f"   验证评分: {validation_result['score']}/100")
        print(f"   是否有效: {validation_result['is_valid']}")
        print(f"   是否有警告: {validation_result['has_warnings']}")
        
        if validation_result['errors']:
            print(f"   ❌ 错误: {validation_result['errors']}")
        if validation_result['warnings']:
            print(f"   ⚠️ 警告: {validation_result['warnings']}")
        if validation_result['suggestions']:
            print(f"   💡 建议: {validation_result['suggestions']}")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_voice_recognition_service():
    """测试语音识别服务"""
    print("\n🔍 测试语音识别服务...")
    
    try:
        from app.services.voice_recognition import voice_recognition_service
        
        print(f"   服务可用性: {voice_recognition_service.is_available()}")
        
        if voice_recognition_service.is_available():
            print("✅ 语音识别服务已配置")
        else:
            print("⚠️ 语音识别服务未配置（需要设置腾讯云凭证）")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试语音功能模块...")
    
    # 测试语音解析器
    test_voice_parser()
    
    # 测试目标验证器
    test_goal_validator()
    
    # 测试语音识别服务
    test_voice_recognition_service()
    
    print("\n✨ 语音功能模块测试完成！")

if __name__ == "__main__":
    main()
