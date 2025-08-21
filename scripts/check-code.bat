@echo off
chcp 65001 >nul
echo 🐍 Python代码规范检查工具
echo ================================

if "%1"=="--fix" (
    echo 🔧 自动修复模式
    python scripts/check-python-code.py --fix
) else (
    echo 🔍 检查模式
    python scripts/check-python-code.py --check
)

echo.
echo 按任意键退出...
pause >nul
