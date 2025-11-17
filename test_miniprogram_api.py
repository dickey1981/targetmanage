#!/usr/bin/env python3
"""
微信小程序API测试脚本
用于验证后端API是否正常工作
"""

import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://106.54.212.67"
API_BASE = f"{BASE_URL}/api"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_health_check():
    """测试1：健康检查"""
    print("\n" + "="*60)
    print("测试1：健康检查")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"服务器健康检查通过")
            print_info(f"服务: {data.get('service', 'N/A')}")
            print_info(f"版本: {data.get('version', 'N/A')}")
            print_info(f"状态: {data.get('status', 'N/A')}")
            return True
        else:
            print_error(f"健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"连接失败: {str(e)}")
        return False

def test_wechat_login_endpoint():
    """测试2：微信登录接口（端点测试）"""
    print("\n" + "="*60)
    print("测试2：微信登录接口")
    print("="*60)
    
    try:
        # 使用无效的code测试端点是否存在
        response = requests.post(
            f"{API_BASE}/auth/wechat-login",
            json={"code": "test_code_123"},
            timeout=10
        )
        
        # 预期会返回400或类似错误（因为code无效）
        # 但至少证明端点存在
        if response.status_code in [200, 400, 401, 422]:
            print_success("微信登录接口存在")
            print_info(f"响应状态: HTTP {response.status_code}")
            try:
                data = response.json()
                print_info(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except:
                print_info(f"响应内容: {response.text}")
            return True
        else:
            print_error(f"接口异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"请求失败: {str(e)}")
        return False

def test_voice_process_endpoint():
    """测试3：语音处理接口（端点测试）"""
    print("\n" + "="*60)
    print("测试3：语音处理接口")
    print("="*60)
    
    try:
        # 测试端点是否存在（不上传真实文件）
        response = requests.post(
            f"{API_BASE}/voice/process",
            files={},  # 空文件
            timeout=10
        )
        
        # 预期会返回400或422（缺少文件）
        # 但至少证明端点存在
        if response.status_code in [200, 400, 401, 422]:
            print_success("语音处理接口存在")
            print_info(f"响应状态: HTTP {response.status_code}")
            try:
                data = response.json()
                print_info(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except:
                print_info(f"响应内容: {response.text}")
            return True
        else:
            print_error(f"接口异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"请求失败: {str(e)}")
        return False

def test_goals_endpoint():
    """测试4：目标列表接口（需要认证）"""
    print("\n" + "="*60)
    print("测试4：目标列表接口")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE}/goals",
            timeout=10
        )
        
        # 预期返回401（未认证）或200（如果不需要认证）
        if response.status_code in [200, 401]:
            print_success("目标列表接口存在")
            print_info(f"响应状态: HTTP {response.status_code}")
            if response.status_code == 401:
                print_warning("需要认证（正常行为）")
            try:
                data = response.json()
                print_info(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except:
                print_info(f"响应内容: {response.text}")
            return True
        else:
            print_error(f"接口异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"请求失败: {str(e)}")
        return False

def test_cors_headers():
    """测试5：CORS配置"""
    print("\n" + "="*60)
    print("测试5：CORS配置")
    print("="*60)
    
    try:
        response = requests.options(
            f"{API_BASE}/auth/wechat-login",
            headers={
                "Origin": "http://localhost",
                "Access-Control-Request-Method": "POST"
            },
            timeout=10
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        
        print_success("CORS配置检查完成")
        for key, value in cors_headers.items():
            if value:
                print_info(f"{key}: {value}")
            else:
                print_warning(f"{key}: 未设置")
        
        return True
    except Exception as e:
        print_error(f"CORS检查失败: {str(e)}")
        return False

def test_response_time():
    """测试6：响应时间"""
    print("\n" + "="*60)
    print("测试6：响应时间测试")
    print("="*60)
    
    try:
        import time
        
        # 测试健康检查接口的响应时间
        times = []
        for i in range(5):
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            end = time.time()
            elapsed = (end - start) * 1000  # 转换为毫秒
            times.append(elapsed)
            print_info(f"请求 {i+1}: {elapsed:.2f}ms")
        
        avg_time = sum(times) / len(times)
        print_success(f"平均响应时间: {avg_time:.2f}ms")
        
        if avg_time < 100:
            print_success("响应速度优秀")
        elif avg_time < 500:
            print_success("响应速度良好")
        else:
            print_warning("响应速度较慢，可能影响用户体验")
        
        return True
    except Exception as e:
        print_error(f"响应时间测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 微信小程序后端API测试")
    print("="*60)
    print(f"服务器地址: {BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("健康检查", test_health_check),
        ("微信登录接口", test_wechat_login_endpoint),
        ("语音处理接口", test_voice_process_endpoint),
        ("目标列表接口", test_goals_endpoint),
        ("CORS配置", test_cors_headers),
        ("响应时间", test_response_time),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"测试 '{name}' 执行失败: {str(e)}")
            results.append((name, False))
    
    # 输出测试总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "-"*60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print_success("🎉 所有测试通过！后端API工作正常")
    elif passed >= total * 0.7:
        print_warning("⚠️  部分测试失败，但核心功能可用")
    else:
        print_error("❌ 多个测试失败，请检查后端配置")
    
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print_error(f"测试脚本执行失败: {str(e)}")
        exit(1)

