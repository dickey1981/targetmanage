@echo off
echo 启动智能目标管理系统开发服务器...
echo.

cd /d "%~dp0"

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 检查依赖...
pip install -r requirements.txt

echo.
echo 启动服务器...
echo 服务地址：http://localhost:8000
echo API文档：http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务器
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
