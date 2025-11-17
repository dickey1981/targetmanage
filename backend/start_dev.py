#!/usr/bin/env python3
"""
快速启动开发服务器
使用腾讯云LightDB MySQL数据库
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 检查并安装依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def start_server():
    """启动开发服务器"""
    print("\n🚀 启动开发服务器...")
    print("🗄️ 使用腾讯云LightDB MySQL数据库")
    print("🔧 开发模式: ASR + OCR（模拟数据）")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("⏹️  停止服务: 按 Ctrl+C")
    print("-" * 50)
    
    # 设置环境变量（必须在启动前设置）
    os.environ['ASR_DEV_MODE'] = 'true'
    os.environ['OCR_DEV_MODE'] = 'true'
    os.environ['DEBUG'] = 'True'
    
    # 打印环境变量确认
    print(f"✅ ASR_DEV_MODE={os.environ.get('ASR_DEV_MODE')}")
    print(f"✅ OCR_DEV_MODE={os.environ.get('OCR_DEV_MODE')}")
    print("-" * 50)
    
    try:
        # 使用uvicorn启动，传递环境变量
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("🎯 智能目标管理系统 - 开发服务器启动器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查依赖
    if not install_dependencies():
        return
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
