"""
智能目标管理系统主应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from .api import auth, user, goals, records, process_records, photo_records
from .config.settings import get_settings

# 导入所有模型以确保它们被正确初始化
from .models import Base, User, Goal, Task, Progress, ProcessRecord

# 获取配置
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 智能目标管理系统启动中...")
    yield
    # 关闭时执行
    print("👋 智能目标管理系统已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="智能目标管理系统",
    description="一个面向个人用户的智能化目标管理服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth.router, tags=["认证"])
app.include_router(user.router, tags=["用户"])
app.include_router(goals.router, tags=["目标"])
app.include_router(records.router, tags=["记录"])
app.include_router(process_records.router, tags=["过程记录"])
app.include_router(photo_records.router, tags=["拍照记录"])

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能目标管理系统API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z",
        "service": "智能目标管理系统",
        "version": "1.0.0"
    }

# 测试接口
@app.get("/api/test")
async def test_api():
    """测试API接口"""
    return {
        "success": True,
        "message": "API连接正常",
        "data": {
            "timestamp": "2025-01-01T00:00:00Z",
            "service": "智能目标管理系统"
        }
    }

# 测试表创建接口
@app.get("/api/test/create-tables")
async def create_tables():
    """创建数据库表（仅用于开发环境）"""
    try:
        from .database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        print("🔨 开始创建数据库表...")
        
        # 创建users表
        print("🔨 创建users表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                wechat_id VARCHAR(100) UNIQUE NOT NULL,
                nickname VARCHAR(100) NOT NULL,
                avatar TEXT,
                phone_number VARCHAR(20),
                email VARCHAR(100),
                notification_enabled BOOLEAN DEFAULT TRUE,
                privacy_level VARCHAR(20) DEFAULT 'public',
                total_goals VARCHAR(10) DEFAULT '0',
                completed_goals VARCHAR(10) DEFAULT '0',
                streak_days VARCHAR(10) DEFAULT '0',
                is_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                is_locked BOOLEAN DEFAULT FALSE,
                locked_until DATETIME,
                failed_login_attempts VARCHAR(10) DEFAULT '0',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login_at DATETIME,
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at DATETIME
            )
        """))
        print("✅ users表创建成功")
        
        # 创建goals表
        print("🔨 创建goals表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50) DEFAULT 'personal',
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'draft',
                start_date DATETIME,
                end_date DATETIME,
                estimated_hours FLOAT,
                progress_percentage FLOAT DEFAULT 0.0,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at DATETIME,
                is_public BOOLEAN DEFAULT FALSE,
                allow_collaboration BOOLEAN DEFAULT FALSE,
                reminder_enabled BOOLEAN DEFAULT TRUE,
                reminder_frequency VARCHAR(20) DEFAULT 'daily',
                user_id VARCHAR(36) NOT NULL,
                parent_goal_id INT,
                total_tasks INT DEFAULT 0,
                completed_tasks INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE
            )
        """))
        print("✅ goals表创建成功")
        
        # 创建user_sessions表
        print("🔨 创建user_sessions表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                refresh_token VARCHAR(255) UNIQUE NOT NULL,
                device_info TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        print("✅ user_sessions表创建成功")
        
        # 创建login_attempts表
        print("🔨 创建login_attempts表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                wechat_id VARCHAR(100),
                phone_number VARCHAR(20),
                ip_address VARCHAR(45),
                user_agent TEXT,
                success BOOLEAN DEFAULT FALSE,
                failure_reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ login_attempts表创建成功")
        
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "数据库表创建成功",
            "data": {
                "tables": ["users", "goals"]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"创建表失败: {str(e)}"
        }

# 查看表结构接口
@app.get("/api/test/show-tables")
async def show_tables():
    """查看数据库表结构（仅用于开发环境）"""
    try:
        from .database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # 查看goals表结构
        result = db.execute(text("DESCRIBE goals"))
        goals_columns = []
        for row in result:
            goals_columns.append({
                "Field": row[0],
                "Type": row[1],
                "Null": row[2],
                "Key": row[3],
                "Default": row[4],
                "Extra": row[5]
            })
        
        # 查看users表结构
        result = db.execute(text("DESCRIBE users"))
        users_columns = []
        for row in result:
            users_columns.append({
                "Field": row[0],
                "Type": row[1],
                "Null": row[2],
                "Key": row[3],
                "Default": row[4],
                "Extra": row[5]
            })
        
        db.close()
        
        return {
            "success": True,
            "message": "表结构查询成功",
            "data": {
                "goals": goals_columns,
                "users": users_columns
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"查询表结构失败: {str(e)}"
        }

# 微信登录测试接口
@app.post("/api/test/wechat-login-test")
async def wechat_login_test():
    """微信登录测试（仅用于开发环境）"""
    try:
        from .database import SessionLocal
        from sqlalchemy import text
        import uuid
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        # 模拟微信用户信息
        wechat_id = f"test_wechat_{uuid.uuid4().hex[:8]}"
        nickname = "测试用户"
        avatar = "https://example.com/avatar.jpg"
        
        # 检查用户是否已存在
        result = db.execute(text("SELECT id FROM users WHERE wechat_id = :wechat_id"), {
            "wechat_id": wechat_id
        })
        existing_user = result.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
            print(f"✅ 用户已存在: {user_id}")
        else:
            # 创建新用户
            user_id = str(uuid.uuid4())
            db.execute(text("""
                INSERT INTO users (id, wechat_id, nickname, avatar, created_at, updated_at)
                VALUES (:user_id, :wechat_id, :nickname, :avatar, NOW(), NOW())
            """), {
                "user_id": user_id,
                "wechat_id": wechat_id,
                "nickname": nickname,
                "avatar": avatar
            })
            print(f"✅ 新用户创建成功: {user_id}")
        
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "微信登录测试成功",
            "data": {
                "user_id": user_id,
                "wechat_id": wechat_id,
                "nickname": nickname
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"微信登录测试失败: {str(e)}"
        }

# Goals查询测试接口
@app.get("/api/test/goals-test")
async def goals_test():
    """Goals查询测试（仅用于开发环境）"""
    try:
        from .database import SessionLocal
        from sqlalchemy import text
        from datetime import datetime
        
        db = SessionLocal()
        
        # 查询所有目标
        result = db.execute(text("SELECT * FROM goals LIMIT 5"))
        goals_data = result.fetchall()
        
        # 查询今日目标
        today = datetime.now().date()
        today_result = db.execute(text("""
            SELECT * FROM goals 
            WHERE target_date = :today
        """), {
            "today": today
        })
        today_goals = today_result.fetchall()
        
        # 测试get_today_goals逻辑（模拟）
        today_goals_formatted = []
        for goal_row in today_goals:
            today_goals_formatted.append({
                "id": str(goal_row[0]),
                "title": goal_row[2],
                "category": goal_row[4] or "其他",
                "progress": 0,
                "completed": False,
                "created_at": str(goal_row[9]) if goal_row[9] else None
            })
        
        # 测试get_all_goals逻辑（模拟）
        all_goals_formatted = []
        for goal_row in goals_data:
            all_goals_formatted.append({
                "id": str(goal_row[0]),
                "title": goal_row[2],
                "category": goal_row[4] or "其他",
                "progress": 0,
                "completed": False,
                "created_at": str(goal_row[9]) if goal_row[9] else None
            })
        
        db.close()
        
        return {
            "success": True,
            "message": "Goals查询测试成功",
            "data": {
                "all_goals_count": len(goals_data),
                "today_goals_count": len(today_goals),
                "sample_goals": [
                    {
                        "id": str(goal[0]),
                        "title": goal[2],
                        "category": goal[4],
                        "target_date": str(goal[8]) if goal[8] else None
                    } for goal in goals_data[:3]
                ],
                "today_goals_formatted": today_goals_formatted,
                "all_goals_formatted": all_goals_formatted
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Goals查询测试失败: {str(e)}"
        }

# 测试数据创建接口
@app.post("/api/test/create-test-data")
async def create_test_data():
    """创建测试数据（仅用于开发环境）"""
    try:
        from .database import SessionLocal
        from sqlalchemy import text
        import uuid
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        # 首先创建表（如果不存在）
        print("🔨 检查并创建数据库表...")
        
        # 创建users表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                wechat_id VARCHAR(100) UNIQUE NOT NULL,
                nickname VARCHAR(100) NOT NULL,
                avatar TEXT,
                phone_number VARCHAR(20),
                email VARCHAR(100),
                notification_enabled BOOLEAN DEFAULT TRUE,
                privacy_level VARCHAR(20) DEFAULT 'public',
                total_goals VARCHAR(10) DEFAULT '0',
                completed_goals VARCHAR(10) DEFAULT '0',
                streak_days VARCHAR(10) DEFAULT '0',
                is_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                is_locked BOOLEAN DEFAULT FALSE,
                locked_until DATETIME,
                failed_login_attempts VARCHAR(10) DEFAULT '0',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login_at DATETIME,
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at DATETIME
            )
        """))
        
        # 创建goals表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50) DEFAULT 'personal',
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'draft',
                start_date DATETIME,
                end_date DATETIME,
                estimated_hours FLOAT,
                progress_percentage FLOAT DEFAULT 0.0,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at DATETIME,
                is_public BOOLEAN DEFAULT FALSE,
                allow_collaboration BOOLEAN DEFAULT FALSE,
                reminder_enabled BOOLEAN DEFAULT TRUE,
                reminder_frequency VARCHAR(20) DEFAULT 'daily',
                user_id VARCHAR(36) NOT NULL,
                parent_goal_id INT,
                total_tasks INT DEFAULT 0,
                completed_tasks INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE
            )
        """))
        
        db.commit()
        print("✅ 数据库表创建成功")
        
        # 创建测试用户
        user_id = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO users (id, wechat_id, nickname, avatar, created_at, updated_at)
            VALUES (:user_id, :wechat_id, :nickname, :avatar, NOW(), NOW())
        """), {
            "user_id": user_id,
            "wechat_id": "test_user_123",
            "nickname": "测试用户",
            "avatar": "https://example.com/avatar.jpg"
        })
        
        # 创建测试目标
        goal_id = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO goals (id, title, description, category, priority, status, 
                              target_date, user_id, created_at, updated_at)
            VALUES (:goal_id, :title, :description, :category, :priority, :status,
                    :target_date, :user_id, NOW(), NOW())
        """), {
            "goal_id": goal_id,
            "title": "学习Python",
            "description": "掌握Python编程基础",
            "category": "study",
            "priority": "medium",
            "status": "active",
            "target_date": (datetime.now() + timedelta(days=30)).date(),
            "user_id": user_id
        })
        
        db.commit()
        db.close()
        
        return {
            "success": True,
            "message": "测试数据创建成功",
            "data": {
                "user_id": user_id,
                "goal_id": goal_id
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"创建测试数据失败: {str(e)}"
        }

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": 500
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
