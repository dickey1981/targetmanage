#!/usr/bin/env python3
"""
Python代码规范检查脚本
用于在Windows环境下替代npm命令进行代码规范检查
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="backend")
        if result.returncode == 0:
            print(f"✅ {description} 通过")
            return True
        else:
            print(f"❌ {description} 失败")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} 执行失败: {e}")
        return False

def check_python_code():
    """检查Python代码规范"""
    print("🐍 开始检查Python代码规范...")
    
    # 检查是否在正确的目录
    if not Path("backend").exists():
        print("❌ 错误: 请在项目根目录下运行此脚本")
        return False
    
    # 检查工具是否安装
    tools = [
        ("black", "black --version"),
        ("isort", "isort --version"),
        ("flake8", "flake8 --version"),
        ("pylint", "pylint --version")
    ]
    
    missing_tools = []
    for tool_name, version_cmd in tools:
        try:
            subprocess.run(version_cmd, shell=True, capture_output=True, cwd="backend")
        except:
            missing_tools.append(tool_name)
    
    if missing_tools:
        print(f"❌ 缺少以下工具: {', '.join(missing_tools)}")
        print("请运行: pip install black isort flake8 pylint")
        return False
    
    # 运行代码规范检查
    checks = [
        ("python -m black --check .", "代码格式化检查"),
        ("python -m isort --check-only .", "导入排序检查"),
        ("python -m flake8 .", "代码质量检查"),
        ("python -m pylint . --score=yes", "代码复杂度检查")
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def fix_python_code():
    """自动修复Python代码规范问题"""
    print("🔧 开始自动修复Python代码规范问题...")
    
    if not Path("backend").exists():
        print("❌ 错误: 请在项目根目录下运行此脚本")
        return False
    
    # 自动修复
    fixes = [
        ("python -m black .", "代码格式化"),
        ("python -m isort .", "导入排序")
    ]
    
    for command, description in fixes:
        print(f"\n🔧 {description}...")
        try:
            result = subprocess.run(command, shell=True, cwd="backend")
            if result.returncode == 0:
                print(f"✅ {description} 完成")
            else:
                print(f"❌ {description} 失败")
        except Exception as e:
            print(f"❌ {description} 执行失败: {e}")
    
    print("\n🔍 修复完成后，请重新运行检查...")

def main():
    parser = argparse.ArgumentParser(description="Python代码规范检查工具")
    parser.add_argument("--fix", action="store_true", help="自动修复代码规范问题")
    parser.add_argument("--check", action="store_true", help="检查代码规范（默认）")
    
    args = parser.parse_args()
    
    if args.fix:
        fix_python_code()
    else:
        if check_python_code():
            print("\n🎉 所有代码规范检查通过！")
            sys.exit(0)
        else:
            print("\n⚠️  代码规范检查未通过，请修复问题后重试")
            print("💡 提示: 使用 --fix 参数可以自动修复部分问题")
            sys.exit(1)

if __name__ == "__main__":
    main()
