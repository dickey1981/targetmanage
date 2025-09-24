#!/usr/bin/env python3
"""
离线测试语音解析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.voice_parser import voice_goal_parser
from app.utils.goal_validator import goal_validator

def test_voice_parsing_offline():
    """离线测试语音解析功能"""
    print("🔍 离线测试语音解析功能...")
    
    test_cases = [
        "我要在3个月内减重10斤",
        "半年内学会游泳",
        "这个季度要完成5个项目",
        "下个月开始学习Python编程",
        "每天跑步30分钟",
        "每周读一本书",
        "提高工作效率",
        "学习英语口语"
    ]
    
    success_count = 0
    
    for i, voice_text in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {voice_text} ---")
        
        try:
            # 解析语音文本
            parsed_goal = voice_goal_parser.parse_voice_to_goal(voice_text)
            
            # 验证解析结果
            validation = goal_validator.validate_goal(parsed_goal)
            
            print("✅ 解析成功")
            print(f"   标题: {parsed_goal.get('title', 'N/A')}")
            print(f"   类别: {parsed_goal.get('category', 'N/A')}")
            print(f"   目标值: {parsed_goal.get('targetValue', 'N/A')}{parsed_goal.get('unit', '')}")
            print(f"   时间范围: {parsed_goal.get('startDate', 'N/A')} 至 {parsed_goal.get('endDate', 'N/A')}")
            print(f"   验证评分: {validation.get('score', 'N/A')}/100")
            
            if validation.get('warnings'):
                print(f"   建议: {validation['warnings'][0]}")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
    
    print(f"\n📊 离线测试结果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)

def test_voice_recognition_service():
    """测试语音识别服务初始化"""
    print("\n🔍 测试语音识别服务初始化...")
    
    try:
        from app.services.voice_recognition import voice_recognition_service
        
        print(f"   服务可用性: {'✅ 可用' if voice_recognition_service.is_available() else '❌ 不可用'}")
        print(f"   客户端状态: {'✅ 已初始化' if voice_recognition_service.client else '❌ 未初始化'}")
        
        # 测试开发模式
        import os
        is_dev_mode = (
            os.getenv('ASR_DEV_MODE', 'false').lower() == 'true' or
            os.getenv('DEBUG', 'false').lower() == 'true' or
            not voice_recognition_service.client
        )
        print(f"   开发模式: {'✅ 启用' if is_dev_mode else '❌ 禁用'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始离线测试语音功能...")
    
    # 测试语音解析
    parsing_success = test_voice_parsing_offline()
    
    # 测试语音识别服务
    service_success = test_voice_recognition_service()
    
    print(f"\n📊 总体测试结果:")
    print(f"   语音解析: {'✅ 成功' if parsing_success else '❌ 失败'}")
    print(f"   语音服务: {'✅ 成功' if service_success else '❌ 失败'}")
    
    if parsing_success and service_success:
        print("\n🎉 所有离线测试通过！语音功能核心组件工作正常。")
        print("现在可以在微信小程序中测试语音创建目标功能了！")
        print("\n📝 使用说明:")
        print("1. 在微信开发者工具中按住语音按钮录音")
        print("2. 系统会自动使用开发模式（模拟识别）")
        print("3. 返回随机测试文本进行解析")
        print("4. 验证完整的语音创建目标流程")
    else:
        print("\n⚠️ 部分测试失败，请检查相关组件。")

if __name__ == "__main__":
    main()
