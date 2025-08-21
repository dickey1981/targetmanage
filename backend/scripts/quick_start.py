#!/usr/bin/env python3
"""
快速启动脚本
用于快速启动目标管理系统后端服务
"""
import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖是否安装"""
    logger.info("检查Python依赖...")
    
    try:
        import fastapi
        import sqlalchemy
        import psycopg2
        import redis
        import jwt
        logger.info("✅ Python依赖检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ Python依赖缺失: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        return False

def check_database():
    """检查数据库连接"""
    logger.info("检查数据库连接...")
    
    try:
        from app.config.settings import get_settings
        from app.database import engine
        
        settings = get_settings()
        logger.info(f"数据库URL: {settings.DATABASE_URL}")
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✅ 数据库连接成功")
            return True
            
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        logger.info("请检查数据库配置和连接")
        return False

def check_redis():
    """检查Redis连接"""
    logger.info("检查Redis连接...")
    
    try:
        from app.config.settings import get_settings
        import redis
        
        settings = get_settings()
        logger.info(f"Redis URL: {settings.REDIS_URL}")
        
        # 测试连接
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        logger.info("✅ Redis连接成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ Redis连接失败: {e}")
        logger.info("请检查Redis配置和连接")
        return False

def run_migrations():
    """运行数据库迁移"""
    logger.info("运行数据库迁移...")
    
    try:
        backend_dir = Path(__file__).parent.parent
        os.chdir(backend_dir)
        
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir
        )
        
        if result.returncode == 0:
            logger.info("✅ 数据库迁移成功")
            return True
        else:
            logger.error(f"❌ 数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 运行迁移失败: {e}")
        return False

def start_server():
    """启动服务器"""
    logger.info("启动FastAPI服务器...")
    
    try:
        backend_dir = Path(__file__).parent.parent
        os.chdir(backend_dir)
        
        # 启动服务器
        cmd = [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        logger.info("服务器启动中...")
        logger.info("访问地址: http://localhost:8000")
        logger.info("API文档: http://localhost:8000/docs")
        logger.info("按 Ctrl+C 停止服务器")
        
        # 启动服务器
        subprocess.run(cmd, cwd=backend_dir)
        
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    logger.info("🚀 目标管理系统后端快速启动")
    logger.info("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查数据库
    if not check_database():
        logger.warning("⚠️  数据库连接失败，但继续启动...")
    
    # 检查Redis
    if not check_redis():
        logger.warning("⚠️  Redis连接失败，但继续启动...")
    
    # 运行迁移
    if not run_migrations():
        logger.warning("⚠️  数据库迁移失败，但继续启动...")
    
    logger.info("=" * 50)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
