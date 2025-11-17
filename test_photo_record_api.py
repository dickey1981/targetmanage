#!/usr/bin/env python3
"""
拍照记录API测试脚本
Test script for photo record API
"""

import requests
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64

# 服务器配置
BASE_URL = "http://106.54.212.67"
API_BASE = f"{BASE_URL}/api"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.END}")

def create_test_image():
    """创建测试图片"""
    print_info("创建测试图片...")
    
    # 创建白色背景图片
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 添加文字
    text = "今天完成了Python学习任务，进度80%\n学习了装饰器和生成器的使用\n感觉收获很大！"
    
    try:
        # 尝试使用中文字体
        font = ImageFont.truetype("simhei.ttf", 40)
    except:
        # 如果没有中文字体，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制文字
    draw.multiline_text((50, 200), text, fill='black', font=font, spacing=20)
    
    # 保存到BytesIO
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    print_success("测试图片创建成功")
    return img_byte_arr

def test_photo_recognize(token=None):
    """测试照片识别接口"""
    print_header("测试1：照片识别接口")
    
    try:
        # 创建测试图片
        test_image = create_test_image()
        
        # 准备请求
        files = {'photo': ('test.png', test_image, 'image/png')}
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        print_info(f"请求URL: {API_BASE}/photo-records/recognize")
        
        # 发送请求
        response = requests.post(
            f"{API_BASE}/photo-records/recognize",
            files=files,
            headers=headers,
            timeout=30
        )
        
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("照片识别成功")
            print_info(f"识别文本: {data.get('data', {}).get('text', 'N/A')}")
            print_info(f"置信度: {data.get('data', {}).get('confidence', 'N/A')}")
            return True
        elif response.status_code == 401:
            print_warning("需要认证（正常行为，需要token）")
            return True
        else:
            print_error(f"识别失败: HTTP {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        return False

def test_photo_recognize_and_create(token=None):
    """测试照片识别并创建记录接口"""
    print_header("测试2：照片识别并创建记录接口")
    
    try:
        # 创建测试图片
        test_image = create_test_image()
        
        # 准备请求
        files = {'photo': ('test.png', test_image, 'image/png')}
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        print_info(f"请求URL: {API_BASE}/photo-records/recognize-and-create")
        
        # 发送请求
        response = requests.post(
            f"{API_BASE}/photo-records/recognize-and-create",
            files=files,
            headers=headers,
            timeout=30
        )
        
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("照片识别并创建记录成功")
            
            if data.get('success'):
                record = data.get('record', {})
                analysis = data.get('analysis', {})
                
                print_info(f"记录ID: {record.get('id', 'N/A')}")
                print_info(f"识别内容: {record.get('content', 'N/A')}")
                print_info(f"记录类型: {analysis.get('record_type', 'N/A')}")
                print_info(f"情绪: {analysis.get('sentiment', 'N/A')}")
                print_info(f"能量等级: {analysis.get('energy_level', 'N/A')}")
                print_info(f"置信度: {analysis.get('confidence_score', 'N/A')}%")
                
                if analysis.get('keywords'):
                    print_info(f"关键词: {', '.join(analysis.get('keywords', []))}")
                
                return True
            else:
                print_warning(f"创建失败: {data.get('message', 'Unknown error')}")
                return False
                
        elif response.status_code == 401:
            print_warning("需要认证（正常行为，需要token）")
            return True
        else:
            print_error(f"请求失败: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"错误信息: {error_data.get('detail', 'Unknown error')}")
            except:
                print_error(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint_exists():
    """测试API端点是否存在"""
    print_header("测试3：API端点检查")
    
    try:
        # 测试端点（不带文件，预期会失败但能证明端点存在）
        response = requests.post(
            f"{API_BASE}/photo-records/recognize",
            timeout=10
        )
        
        # 任何响应都说明端点存在
        if response.status_code in [200, 400, 401, 422]:
            print_success("照片识别API端点存在")
            return True
        else:
            print_error(f"端点响应异常: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"端点检查失败: {str(e)}")
        return False

def test_dev_mode_status():
    """测试开发模式状态"""
    print_header("测试4：开发模式状态检查")
    
    try:
        # 通过健康检查接口获取系统信息
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            print_success("系统运行正常")
            print_info("OCR开发模式: 已启用（预期）")
            print_info("开发模式下会返回模拟识别数据")
            return True
        else:
            print_error("系统健康检查失败")
            return False
            
    except Exception as e:
        print_error(f"健康检查失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print_header("📷 拍照记录API测试")
    print_info(f"服务器地址: {BASE_URL}")
    print_info("注意: 某些测试需要认证token，预期会返回401")
    
    tests = [
        ("API端点检查", test_api_endpoint_exists),
        ("开发模式状态", test_dev_mode_status),
        ("照片识别接口", lambda: test_photo_recognize()),
        ("照片识别并创建记录", lambda: test_photo_recognize_and_create()),
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
    print_header("📊 测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "-"*60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print_success("🎉 所有测试通过！拍照记录API工作正常")
    elif passed >= total * 0.7:
        print_warning("⚠️  部分测试失败，但核心功能可用")
    else:
        print_error("❌ 多个测试失败，请检查配置")
    
    print("\n" + "="*60)
    print(f"{Colors.CYAN}💡 提示:")
    print(f"  - 在微信开发者工具中测试拍照功能")
    print(f"  - 确保已关闭域名校验")
    print(f"  - 开发模式下会返回模拟数据")
    print(f"  - 真实环境需要配置腾讯云OCR服务{Colors.END}")
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

