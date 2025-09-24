#!/usr/bin/env python3
"""
测试语音识别开发模式
"""

import requests
import json
import os

def test_voice_recognition_dev_mode():
    """测试语音识别开发模式"""
    print("🔍 测试语音识别开发模式...")
    
    base_url = "http://localhost:8000"
    
    # 测试语音识别端点
    try:
        # 创建一个模拟的音频文件（实际测试中会使用真实录音）
        mock_audio_data = b"mock audio data for testing"
        
        # 模拟上传文件请求
        files = {
            'audio': ('test.mp3', mock_audio_data, 'audio/mp3')
        }
        
        response = requests.post(
            f"{base_url}/api/goals/test-voice-recognition",
            files=files,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 语音识别成功: {data.get('data', {}).get('text', 'N/A')}")
                return True
            else:
                print(f"❌ 语音识别失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_voice_parsing():
    """测试语音解析功能"""
    print("\n🔍 测试语音解析功能...")
    
    base_url = "http://localhost:8000"
    test_voice_text = "我要在3个月内减重10斤"
    
    try:
        response = requests.post(
            f"{base_url}/api/goals/test-parse-voice",
            json={"voice_text": test_voice_text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                parsed_data = data.get('data', {})
                validation = data.get('validation', {})
                
                print("✅ 语音解析成功")
                print(f"   标题: {parsed_data.get('title', 'N/A')}")
                print(f"   类别: {parsed_data.get('category', 'N/A')}")
                print(f"   目标值: {parsed_data.get('targetValue', 'N/A')}{parsed_data.get('unit', '')}")
                print(f"   时间范围: {parsed_data.get('startDate', 'N/A')} 至 {parsed_data.get('endDate', 'N/A')}")
                print(f"   验证评分: {validation.get('score', 'N/A')}/100")
                return True
            else:
                print(f"❌ 语音解析失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试语音功能开发模式...")
    
    # 测试语音识别
    recognition_success = test_voice_recognition_dev_mode()
    
    # 测试语音解析
    parsing_success = test_voice_parsing()
    
    print(f"\n📊 测试结果:")
    print(f"   语音识别: {'✅ 成功' if recognition_success else '❌ 失败'}")
    print(f"   语音解析: {'✅ 成功' if parsing_success else '❌ 失败'}")
    
    if recognition_success and parsing_success:
        print("\n🎉 所有测试通过！语音功能开发模式工作正常。")
        print("现在可以在微信小程序中测试语音创建目标功能了！")
    else:
        print("\n⚠️ 部分测试失败，请检查后端服务状态。")

if __name__ == "__main__":
    main()
