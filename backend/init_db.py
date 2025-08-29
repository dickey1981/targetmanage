#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建goals表和其他必要的表
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

print("🔍 开始初始化数据库...")
print(f"🔍 当前工作目录: {os.getcwd()}")
print(f"🔍 Python路径: {sys.path}")

try:
    from app.config.settings import get_settings
    print("✅ 成功导入settings模块")
except ImportError as e:
    print(f"❌ 导入settings模块失败: {e}")
    sys.exit(1)

try:
    from app.models.base import Base
    print("✅ 成功导入Base模型")
except ImportError as e:
    print(f"❌ 导入Base模型失败: {e}")
    sys.exit(1)

try:
    from app.models.goal import Goal
    print("✅ 成功导入Goal模型")
except ImportError as e:
    print(f"❌ 导入Goal模型失败: {e}")
    sys.exit(1)

try:
    from app.models.user import User
    print("✅ 成功导入User模型")
except ImportError as e:
    print(f"❌ 导入User模型失败: {e}")
    sys.exit(1)

def init_database():
    """初始化数据库"""
    try:
        # 获取配置
        print("🔍 获取数据库配置...")
        settings = get_settings()
        database_url = settings.DATABASE_URL
        
        print(f"🔍 数据库URL: {database_url}")
        
        # 创建数据库引擎
        print("🔍 创建数据库引擎...")
        engine = create_engine(database_url)
        
        # 测试连接
        print("🔍 测试数据库连接...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
        
        # 创建所有表
        print("🔨 开始创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 验证表是否创建成功
        print("🔍 验证表创建结果...")
        with engine.connect() as conn:
            # 检查goals表
            result = conn.execute(text("SHOW TABLES LIKE 'goals'"))
            if result.fetchone():
                print("✅ goals表创建成功")
            else:
                print("❌ goals表创建失败")
            
            # 检查users表
            result = conn.execute(text("SHOW TABLES LIKE 'users'"))
            if result.fetchone():
                print("✅ users表创建成功")
            else:
                print("❌ users表创建失败")
        
        print("🎉 数据库初始化完成！")
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库操作失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 启动数据库初始化脚本...")
    init_database()
    print("✅ 脚本执行完成")
